import { useState, useRef } from 'react';

export function ImageProcessingSection({ scrollHandler }) {
  const [uploadedImage, setUploadedImage] = useState(null);
  const [processedImage, setProcessedImage] = useState(null);
  const [fileName, setFileName] = useState('Прикрепите файл');
  const [isProcessing, setIsProcessing] = useState(false);
  const [showResult, setShowResult] = useState(false);
  const [showActions, setShowActions] = useState(false);
  const [file, setFile] = useState(null);
  
  const fileInputRef = useRef(null);
  const processedImageRef = useRef(null);

  const API_URL = 'http://localhost:8000/cloud-remove/';

  // Стили для контейнеров
  const containerStyle = {
    width: '500px',
    height: '400px',
    position: 'relative',
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
      };
      reader.readAsDataURL(file);
    }
  };

  const processImage = async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(API_URL, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Ошибка обработки изображения');
    }

    return await response.blob();
  };

  const handleGenerate = async () => {
    if (!file) {
      alert('Пожалуйста, сначала загрузите изображение');
      return;
    }

    setShowResult(false);
    setShowActions(false);
    setIsProcessing(true);

    try {
      const blob = await processImage(file);
      const processedImageUrl = URL.createObjectURL(blob);
      setProcessedImage(processedImageUrl);
      
      setShowResult(true);
      setShowActions(true);
    } catch (error) {
      console.error('Ошибка:', error);
      alert(error.message);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReprocess = async () => {
    if (!file) return;

    setShowResult(false);
    setShowActions(false);
    setIsProcessing(true);

    try {
      const blob = await processImage(file);
      const processedImageUrl = URL.createObjectURL(blob);
      setProcessedImage(processedImageUrl);
      
      setShowResult(true);
      setShowActions(true);
    } catch (error) {
      console.error('Ошибка:', error);
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
                type="file"
                id="file-input"
                className="file-input"
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
            <div className="result-box">
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
                      objectFit: 'cover'
                    }}
                  />
                </div>
              )}

              {showActions && (
                <div className="action-buttons">
                  <button className="like-btn" title="Нравится">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                      <path d="M8 1.314C12.438-3.248 23.534 4.735 8 15-7.534 4.736 3.562-3.248 8 1.314"/>
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