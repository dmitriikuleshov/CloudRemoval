import os
import csv
import argparse

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from torchvision import transforms


class MetaEncoder(nn.Module):
    def __init__(self, meta_dim=3, film_dim=48):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(meta_dim, film_dim),
            nn.ReLU(inplace=True),
            nn.Linear(film_dim, film_dim * 2)
        )

    def forward(self, meta):
        film = self.net(meta)
        gamma, beta = film.chunk(2, dim=1)
        return gamma, beta

class CondLayerNorm(nn.Module):
    def __init__(self, dim, eps=1e-6):
        super().__init__()
        self.ln = nn.LayerNorm(dim, eps=eps)

    def forward(self, x, gamma, beta):
        B, C, H, W = x.shape
        x_flat = x.permute(0,2,3,1).reshape(-1, C)
        x_norm = self.ln(x_flat)
        x_norm = x_norm.reshape(B, H, W, C).permute(0,3,1,2)
        gamma = gamma.view(B, C, 1, 1)
        beta  = beta.view(B, C, 1, 1)
        return gamma * x_norm + beta

class WindowAttention(nn.Module):
    def __init__(self, dim, window_size=8, num_heads=8):
        super().__init__()
        self.dim = dim
        self.window_size = window_size
        self.num_heads = num_heads
        head_dim = dim // num_heads
        self.scale = head_dim ** -0.5
        self.qkv = nn.Conv2d(dim, dim*3, 1, bias=True)
        self.proj = nn.Conv2d(dim, dim, 1)
        coord = torch.stack(torch.meshgrid(
            torch.arange(window_size),
            torch.arange(window_size),
            indexing='ij'
        ))
        coord_flat = coord.flatten(1)
        rel = coord_flat[:, :, None] - coord_flat[:, None, :]
        rel = rel.permute(1,2,0)
        rel[:, :, 0] += window_size - 1
        rel[:, :, 1] += window_size - 1
        rel[:, :, 0] *= 2*window_size - 1
        index = rel.sum(-1)
        self.register_buffer('rel_index', index)
        self.rel_bias = nn.Parameter(torch.zeros((2*window_size-1)**2, num_heads))
        nn.init.trunc_normal_(self.rel_bias, std=0.02)

    def forward(self, x):
        B,C,H,W = x.shape
        ws = self.window_size
        pad_h = (ws - H%ws) % ws
        pad_w = (ws - W%ws) % ws
        x = F.pad(x, (0,pad_w,0,pad_h))
        Hp, Wp = H+pad_h, W+pad_w
        xw = x.view(B, C, Hp//ws, ws, Wp//ws, ws)
        xw = xw.permute(0,2,4,1,3,5).reshape(-1, C, ws, ws)
        qkv = self.qkv(xw).chunk(3,1)
        q = qkv[0].reshape(-1, self.num_heads, C//self.num_heads, ws*ws).transpose(-2,-1)
        k = qkv[1].reshape(-1, self.num_heads, C//self.num_heads, ws*ws)
        v = qkv[2].reshape(-1, self.num_heads, C//self.num_heads, ws*ws).transpose(-2,-1)
        attn = (q @ k) * self.scale
        bias = self.rel_bias[self.rel_index.view(-1)].view(ws*ws, ws*ws, -1)
        bias = bias.permute(2,0,1).unsqueeze(0)
        attn = (attn + bias).softmax(-1)
        out = (attn @ v).transpose(-2,-1).reshape(-1,C,ws,ws)
        out = out.view(B, Hp//ws, Wp//ws, C, ws, ws)
        out = out.permute(0,3,1,4,2,5).reshape(B,C,Hp,Wp)
        return self.proj(out[:,:,:H,:W])

class ShiftedWindowAttention(WindowAttention):
    def __init__(self, dim, window_size=8, num_heads=8):
        super().__init__(dim, window_size, num_heads)
        self.shift = window_size // 2

    def forward(self, x):
        x_shifted = torch.roll(x, shifts=(-self.shift, -self.shift), dims=(2,3))
        out = super().forward(x_shifted)
        return torch.roll(out, shifts=( self.shift,  self.shift), dims=(2,3))

class CrossAttention(nn.Module):
    def __init__(self, dim, num_heads=8, window_size=8):
        super().__init__()
        self.num_heads = num_heads
        self.window_size = window_size
        head_dim = dim // num_heads
        self.scale = head_dim ** -0.5
        self.to_q = nn.Conv2d(dim, dim, 1, bias=False)
        self.to_kv = nn.Conv2d(dim, dim*2, 1, bias=False)
        self.proj = nn.Conv2d(dim, dim, 1)

    def forward(self, x_q, x_kv):
        B,C,H,W = x_q.shape
        ws = self.window_size
        pad_h = (ws - H%ws)%ws; pad_w = (ws - W%ws)%ws
        xq = F.pad(x_q, (0,pad_w,0,pad_h))
        xk = F.pad(x_kv, (0,pad_w,0,pad_h))
        Hn, Wn = H+pad_h, W+pad_w
        xq_w = xq.view(B, C, Hn//ws, ws, Wn//ws, ws).permute(0,2,4,1,3,5).reshape(-1, C, ws, ws)
        xk_w = xk.view(B, C, Hn//ws, ws, Wn//ws, ws).permute(0,2,4,1,3,5).reshape(-1, C, ws, ws)
        q = self.to_q(xq_w).reshape(-1, self.num_heads, C//self.num_heads, ws*ws).transpose(-2, -1)
        kv = self.to_kv(xk_w).reshape(-1, 2, self.num_heads, C//self.num_heads, ws*ws)
        k, v = kv[:,0], kv[:,1]
        v = v.transpose(-2, -1)
        attn = (q @ k) * self.scale
        attn = attn.softmax(-1)
        out = (attn @ v).transpose(-2,-1).reshape(-1, C, ws, ws)
        out = out.view(B, Hn//ws, Wn//ws, C, ws, ws)
        out = out.permute(0,3,1,4,2,5).reshape(B, C, Hn, Wn)
        return self.proj(out[:, :, :H, :W])

class GlobalMDTA(nn.Module):
    def __init__(self, dim, num_heads=8):
        super().__init__()
        self.num_heads = num_heads
        head_dim = dim // num_heads
        self.scale = head_dim ** -0.5
        self.qkv = nn.Conv2d(dim, dim*3, 1, bias=False)
        self.proj = nn.Conv2d(dim, dim, 1)

    def forward(self, x):
        B, C, H, W = x.shape
        qkv = self.qkv(x)
        q, k, v = qkv.chunk(3, dim=1)
        q = q.reshape(B, self.num_heads, C//self.num_heads, H*W).transpose(-2, -1)
        k = k.reshape(B, self.num_heads, C//self.num_heads, H*W)
        v = v.reshape(B, self.num_heads, C//self.num_heads, H*W).transpose(-2, -1)
        attn = (q @ k) * self.scale
        attn = attn.softmax(-1)
        out = attn @ v
        out = out.transpose(-2, -1).reshape(B, C, H, W)
        return self.proj(out)

class FusionRestormerBlock(nn.Module):
    def __init__(self, dim, heads, window_size, ff, use_shift=False):
        super().__init__()
        self.norm1 = CondLayerNorm(dim)
        Attn = ShiftedWindowAttention if use_shift else WindowAttention
        self.attn1 = Attn(dim, window_size, heads)
        self.cross = CrossAttention(dim, heads, window_size)
        self.norm2 = CondLayerNorm(dim)
        self.ffn   = nn.Sequential(
            nn.Conv2d(dim, dim*ff*2, 1, bias=False),
            nn.GELU(),
            nn.Conv2d(dim*ff*2, dim, 1, bias=False)
        )

    def forward(self, x_rgb, x_sar, gamma, beta):
        y  = self.attn1(self.norm1(x_rgb, gamma, beta))
        x1 = x_rgb + y
        y2 = self.cross(self.norm1(x1, gamma, beta), x_sar)
        x2 = x1 + y2
        y3 = self.ffn(self.norm2(x2, gamma, beta))
        return x2 + y3

class FusionGlobalBlock(nn.Module):
    def __init__(self, dim, heads, ff):
        super().__init__()
        self.norm1 = CondLayerNorm(dim)
        self.attn  = GlobalMDTA(dim, heads)
        self.norm2 = CondLayerNorm(dim)
        self.ffn   = nn.Sequential(
            nn.Conv2d(dim, dim*ff*2, 1, bias=False),
            nn.GELU(),
            nn.Conv2d(dim*ff*2, dim, 1, bias=False)
        )

    def forward(self, x, gamma, beta):
        x1 = x + self.attn(self.norm1(x, gamma, beta))
        return x1 + self.ffn(self.norm2(x1, gamma, beta))

class Downsample(nn.Module):
    def __init__(self, in_ch, out_ch):
        super().__init__()
        self.unshuffle = nn.PixelUnshuffle(2)
        self.conv = nn.Conv2d(in_ch * 4, out_ch, 1, bias=False)

    def forward(self, x):
        return self.conv(self.unshuffle(x))

class Upsample(nn.Module):
    def __init__(self, in_ch, out_ch):
        super().__init__()
        self.shuffle = nn.PixelShuffle(2)
        self.conv = nn.Conv2d(in_ch // 4 + out_ch, out_ch, 1, bias=False)

    def forward(self, x, skip):
        return self.conv(torch.cat([self.shuffle(x), skip], dim=1))

class RestormerFusion(nn.Module):
    def __init__(self, in_ch=3, out_ch=3, dim=48,
                 blocks=[4,6,6,8], heads=[1,2,4,8], window_size=8, ff=2, ref=4):
        super().__init__()
        dims = [dim * (2**i) for i in range(len(blocks))]
        self.meta_encs = nn.ModuleList([MetaEncoder(3, d) for d in dims])
        self.shallow_rgb = nn.Conv2d(in_ch, dims[0], 3, padding=1, bias=False)
        self.shallow_sar = nn.Conv2d(in_ch, dims[0], 3, padding=1, bias=False)
        self.encs = nn.ModuleList()
        for i, n_blk in enumerate(blocks):
            use_shift = (i % 2 == 1)
            stage = nn.ModuleList([FusionRestormerBlock(dims[i], heads[i], window_size, ff, use_shift)
                                    for _ in range(n_blk)])
            self.encs.append(stage)
        self.downs = nn.ModuleList([Downsample(dims[i], dims[i+1]) for i in range(len(blocks)-1)])
        self.bottleneck = nn.ModuleList([FusionGlobalBlock(dims[-1], heads[-1], ff) for _ in range(ref)])
        self.ups = nn.ModuleList([Upsample(dims[i+1], dims[i]) for i in reversed(range(len(blocks)-1))])
        self.decs = nn.ModuleList()
        for rev_i, n_blk in enumerate(reversed(blocks[:-1])):
            enc_i = len(blocks)-2-rev_i
            use_shift = (enc_i % 2 == 1)
            stage = nn.ModuleList([FusionRestormerBlock(dims[enc_i], heads[enc_i], window_size, ff, use_shift)
                                    for _ in range(n_blk)])
            self.decs.append(stage)
        self.output = nn.Conv2d(dims[0], out_ch, 3, padding=1, bias=False)

    def forward(self, rgb, sar, meta):
        x_rgb = self.shallow_rgb(rgb)
        x_sar = self.shallow_sar(sar)
        skips = []
        for i, stage in enumerate(self.encs):
            gamma, beta = self.meta_encs[i](meta)
            for blk in stage:
                x_rgb = blk(x_rgb, x_sar, gamma, beta)
                x_sar = blk(x_sar, x_sar, gamma, beta)
            if i < len(self.downs):
                skips.append(x_sar)
                x_rgb = self.downs[i](x_rgb)
                x_sar = self.downs[i](x_sar)
        gamma, beta = self.meta_encs[-1](meta)
        for blk in self.bottleneck:
            x_rgb = blk(x_rgb, gamma, beta)
        for j, up in enumerate(self.ups):
            level = len(self.ups)-1-j
            gamma, beta = self.meta_encs[level](meta)
            x_rgb = up(x_rgb, skips[level])
            for blk in self.decs[j]:
                x_rgb = blk(x_rgb, skips[level], gamma, beta)
        out = self.output(x_rgb)
        return torch.sigmoid(out)
