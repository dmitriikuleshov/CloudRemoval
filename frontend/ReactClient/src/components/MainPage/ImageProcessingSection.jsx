import { useState, useRef } from 'react';
import { useAuth } from '../context/AuthContext';

export function ImageProcessingSection({ scrollHandler }) {
  const containerStyle = {
    width: '500px',
    height: '400px',
    position: 'relative',
  };
  const [uploadedImage, setUploadedImage] = useState(null);
  const [processedImage, setProcessedImage] = useState(null);
  const [fileName, setFileName] = useState('Прикрепите файл');
  const [isProcessing, setIsProcessing] = useState(false);
  const [showResult, setShowResult] = useState(false);
  const [showActions, setShowActions] = useState(false);
  const [file, setFile] = useState(null);
  const [entryId, setEntryId] = useState(null);
  const { user, loading } = useAuth();
  const fileInputRef = useRef(null);
  const processedImageRef = useRef(null);

  const handleDownload = async () => {
    try {
      if (!processedImage) {
        alert('Сначала обработайте изображение');
        return;
      }
  
      const response = await fetch(processedImage);
      
      if (!response.ok) throw new Error('Ошибка загрузки изображения');
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      
      const link = document.createElement('a');
      link.href = url;
      link.download = `processed-image-${Date.now()}.${blob.type.split('/')[1]}`;
      
      document.body.appendChild(link);
      link.click();
      
      window.URL.revokeObjectURL(url);
      document.body.removeChild(link);
    } catch (error) {
      console.error('Ошибка скачивания:', error);
      alert(error.message);
    }
  };

  const getUploadUrl = async () => {
    const response = await fetch('http://37.252.19.60:8000/storage', {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Ошибка получения URL загрузки');
    }
    return await response.json();
  };

  const uploadToS3 = async (url, file) => {
    const response = await fetch(url, {
      method: 'PUT',
      headers: {
        'Content-Type': 'image/png',
        'x-amz-acl': 'private'
      },
      body: file
    });
    if (!response.ok) throw new Error('Ошибка загрузки файла');
  };

  const triggerCloudRemove = async (entryId) => {
    const response = await fetch(`http://37.252.19.60:8000/cloud-remove/?entry=${entryId}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Ошибка запуска обработки');
    }
  };

  const fetchEntryInfo = async (entryId) => {
    const response = await fetch(`http://37.252.19.60:8000/storage/${entryId}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    });
    if (!response.ok) throw new Error('Ошибка получения статуса');
    return await response.json();
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        setUploadedImage(event.target.result);
        setFileName(file.name);
        setFile(file);
        setProcessedImage(null);
        setEntryId(null);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleGenerate = async () => {
    if (!file) {
      alert('Пожалуйста, загрузите изображение');
      return;
    }
  
    setIsProcessing(true);
    setShowResult(false);
    setShowActions(false);
  
    try {
      const uploadResponse = await fetch('http://37.252.19.60:8000/storage', {
        method: 'PUT',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
      });
      
      if (!uploadResponse.ok) throw new Error('Ошибка получения ссылки загрузки');
      const { url: uploadUrl, entry: entryId } = await uploadResponse.json();
      setEntryId(entryId);
  
      await fetch(uploadUrl, {
        method: 'PUT',
        headers: {
          'Content-Type': 'image/png',
          'x-amz-acl': 'private',
        },
        body: file,
      });
  
      const processResponse = await fetch(
        `http://37.252.19.60:8000/cloud-remove?entry=${entryId}`,
        {
          method: 'GET',
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`,
          },
        }
      );
  
      if (!processResponse.ok) throw new Error('Ошибка запуска обработки');
  
      const entryInfo = await fetch(
        `http://37.252.19.60:8000/storage/${entryId}`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`,
          },
        }
      ).then((res) => res.json());
  
      if (!entryInfo.result_url) throw new Error('Результат недоступен');
      setProcessedImage(entryInfo.result_url);
      setShowResult(true);
      setShowActions(true);
    } catch (error) {
      alert(error.message);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReprocess = async () => {
    if (!entryId) return;

    setIsProcessing(true);
    setShowResult(false);
    setShowActions(false);

    try {
      await triggerCloudRemove(entryId);

      let entryInfo;
      let attempts = 0;
      const maxAttempts = 10;
      const delay = 2000;

      while (attempts < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, delay));
        entryInfo = await fetchEntryInfo(entryId);
        if (entryInfo.success) break;
        attempts++;
      }

      if (!entryInfo?.success) {
        throw new Error('Обработка не завершена');
      }

      setProcessedImage(entryInfo.result_url);
      setShowResult(true);
      setShowActions(true);
    } catch (error) {
      alert(error.message);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <section id="image_processing">
      <div className="container">
        <h2 className="text-center">Обработка изображений</h2>
        
        <div className="image-processing-container">
          {/* Контейнер для загрузки */}
          <div className="upload-container" style={containerStyle}>
            <div 
              className="dropzone"
              style={{
                backgroundImage: `url(${uploadedImage})`,
                backgroundRepeat: 'no-repeat',
                backgroundPosition: 'top',
                backgroundSize: 'contain',
              }}
            >
              <input
                disabled={!user || loading}
                type="file"
                id="file-input"
                className= {user ? 'file-input' : 'file-input disabled'}
                accept="image/*"
                onChange={handleFileUpload}
                ref={fileInputRef}
              />
              <label 
                htmlFor="file-input" 
                className="file-input-label"
              >
                {!uploadedImage && (
                  <div className="upload-icon text-center">
                    <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" fill="currentColor" viewBox="0 0 16 16">
                      <path d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"/>
                      <path d="M7.646 1.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1-.708.708L8.5 2.707V11.5a.5.5 0 0 1-1 0V2.707L5.354 4.854a.5.5 0 1 1-.708-.708l3-3z"/>
                    </svg>
                  </div>
                )}
                {uploadedImage ? 'Изменить изображение' : fileName}
              </label>
            </div>
          </div>

          {/* Контейнер для результата */}
          <div className="result-container" style={containerStyle}>
            <div className="result-box" style={{ 
              width: "100%", 
              height: "100%", 
              position: "absolute" 
            }}>
              {!showResult && (
                <p className="result-placeholder">Результат обработки</p>
              )}

              {isProcessing && (
                <div className="processing-indicator">
                  <div className="spinner"></div>
                  <p>Обработка изображения...</p>
                </div>
              )}

              {showResult && (
                <div className="processed-result">
                  <img
                    ref={processedImageRef}
                    src={processedImage}
                    alt="Обработанное изображение"
                    style={{
                      width: '100%',
                      height: '100%',
                      position: 'relative',
                      objectFit: 'cover'
                    }}
                  />
                </div>
              )}

              {showActions && (
                <div className="action-buttons">
                  <button 
                    className="download-btn" 
                    title="Скачать изображение"
                    onClick={handleDownload}
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
                      <path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/>
                    </svg>
                  </button>
                  <button 
                    className="reprocess-btn" 
                    title="Обработать заново"
                    onClick={handleReprocess}
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                      <path d="M11.534 7h3.932a.25.25 0 0 1 .192.41l-1.966 2.36a.25.25 0 0 1-.384 0l-1.966-2.36a.25.25 0 0 1 .192-.41zm-11 2h3.932a.25.25 0 0 0 .192-.41L2.692 6.23a.25.25 0 0 0-.384 0L.342 8.59A.25.25 0 0 0 .534 9z"/>
                      <path fillRule="evenodd" d="M8 3c-1.552 0-2.94.707-3.857 1.818a.5.5 0 1 1-.771-.636A6.002 6.002 0 0 1 13.917 7H12.9A5.002 5.002 0 0 0 8 3M3.1 9a5.002 5.002 0 0 0 8.757 2.182a.5.5 0 1 1 .771.636A6.002 6.002 0 0 1 2.083 9z"/>
                    </svg>
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="generate-btn-container">
          <button 
            className="generate-btn" 
            onClick={handleGenerate}
            disabled={!uploadedImage || isProcessing}
          >
            {isProcessing ? 'Обработка...' : 'Generate'}
          </button>
        </div>
      </div>
      
      <div className="bottom-center">
        <button className="scroll-down" onClick={() => scrollHandler(3)}>
          ▼
        </button>
      </div>
    </section>
  );
}