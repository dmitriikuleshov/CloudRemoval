import { useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import '../../static/css/auth.css';
import backgroundImage from '../../static/videos/1479.gif';

export function AuthPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [activeForm, setActiveForm] = useState('signIn');
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    name: '',
    surname: ''
  });
  const [error, setError] = useState('');

  const handleFormSwitch = (form) => {
    setActiveForm(form);
    setFormData({ username: '', email: '', password: '', name: '', surname: '' });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      if (activeForm === 'signIn') {
        const params = new URLSearchParams();
        params.append('grant_type', 'password');
        params.append('username', formData.username);
        params.append('password', formData.password);
        params.append('client_id', 'string');
        params.append('client_secret', 'string');

        const response = await fetch('http://127.0.0.1:8080/auth/login', {
          method: 'POST',
          headers: {
            'accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
          },
          body: params
        });

        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(errorText || 'Login failed');
        }

        const data = await response.json();
        login(data.access_token);
        navigate('/');
      } else {
        const registrationData = {
          username: formData.username,
          password: formData.password,
          email: formData.email,
          name: formData.name,
          surname: formData.surname
        };

        const response = await fetch('http://127.0.0.1:8080/auth/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(registrationData),
        });

        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(errorText || 'Registration failed');
        }

        handleFormSwitch('signIn');
      }
    } catch (err) {
      setError(err.message);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.id]: e.target.value
    });
  };

  return (
    <div style={{
      position: 'absolute',
      top: 0,
      left: 0,
      background: `url(${backgroundImage})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      minHeight: '100vh',
      minWidth: '100vw',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    }}>
      {error && (
        <div className="alert alert-danger" style={{
          position: 'absolute',
          top: '10px',
          left: '50%',
          transform: 'translateX(-50%)',
          zIndex: 9999
        }}>
          {error}
        </div>
      )}

      <div className="login-container">
        <div className="nav-links">
          <button 
            className={`nav-link ${activeForm === 'signIn' ? 'active' : ''}`}
            onClick={() => handleFormSwitch('signIn')}
          >
            SIGN IN
          </button>
          <button 
            className={`nav-link ${activeForm === 'signUp' ? 'active' : ''}`}
            onClick={() => handleFormSwitch('signUp')}
          >
            SIGN UP
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          {activeForm === 'signIn' ? (
            <>
              <div className="mb-3">
                <label htmlFor="username" className="form-label">USERNAME</label>
                <input
                  type="text"
                  id="username"
                  className="form-control"
                  value={formData.username}
                  onChange={handleChange}
                  required
                />
              </div>
              <div className="mb-3">
                <label htmlFor="password" className="form-label">PASSWORD</label>
                <input
                  type="password"
                  id="password"
                  className="form-control"
                  value={formData.password}
                  onChange={handleChange}
                  required
                />
              </div>
            </>
          ) : (
            <>
              <div className="mb-3">
                <label htmlFor="username" className="form-label">USERNAME</label>
                <input
                  type="text"
                  id="username"
                  className="form-control"
                  value={formData.username}
                  onChange={handleChange}
                  required
                />
              </div>
              <div className="mb-3">
                <label htmlFor="name" className="form-label">NAME</label>
                <input
                  type="text"
                  id="name"
                  className="form-control"
                  value={formData.name}
                  onChange={handleChange}
                  required
                />
              </div>
              <div className="mb-3">
                <label htmlFor="surname" className="form-label">SURNAME</label>
                <input
                  type="text"
                  id="surname"
                  className="form-control"
                  value={formData.surname}
                  onChange={handleChange}
                  required
                />
              </div>
              <div className="mb-3">
                <label htmlFor="email" className="form-label">EMAIL</label>
                <input
                  type="email"
                  id="email"
                  className="form-control"
                  value={formData.email}
                  onChange={handleChange}
                  required
                />
              </div>
              <div className="mb-3">
                <label htmlFor="password" className="form-label">PASSWORD</label>
                <input
                  type="password"
                  id="password"
                  className="form-control"
                  value={formData.password}
                  onChange={handleChange}
                  required
                />
              </div>
            </>
          )}

          <button 
            type="submit" 
            className="btn btn-primary"
          >
            {activeForm === 'signIn' ? 'SIGN IN' : 'SIGN UP'}
          </button>
        </form>

        <p className="forgot-password mt-3">
          <a href="#forgot">Forgot your password?</a>
        </p>
      </div>
    </div>
  );
}