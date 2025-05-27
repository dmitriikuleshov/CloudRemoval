import { useState, useEffect } from 'react';
import { backend_url } from '../../backend_url';

export function SarSection({ scrollHandler }) {
    const [startDate, setStartDate] = useState('');
    const [endDate, setEndDate] = useState('');
    const [coords, setCoords] = useState([0, 0]); // [longitude, latitude]
    const [entryData, setEntryData] = useState({
        source_url: null,
        sar_url: null,
        result_url: null,
    });
    const [entryId, setEntryId] = useState(null);
    const [isProcessing, setIsProcessing] = useState(false);
    const [showResult, setShowResult] = useState(false);

    useEffect(() => {
        const today = new Date().toISOString().split('T')[0];
        const tomorrow = new Date(Date.now() + 86400000).toISOString().split('T')[0];
        setStartDate(today);
        setEndDate(tomorrow);
    }, []);

    const handleCoordChange = (index, value) => {
        const newCoords = [...coords];
        newCoords[index] = parseFloat(value) || 0;
        setCoords(newCoords);
    };

    const fetchEntryStatus = async (entryId) => {
        const response = await fetch(backend_url + `/storage/${entryId}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });
        if (!response.ok) throw new Error('Ошибка получения статуса');
        return await response.json();
    };

    const processEntry = async (entryId) => {
        let attempts = 0;
        const maxAttempts = 20;
        const delay = 3000;

        await fetch(backend_url + `/cloud-remove/v2?entry=${entryId}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });

        while (attempts < maxAttempts) {
            await new Promise(resolve => setTimeout(resolve, delay));
            const entryInfo = await fetchEntryStatus(entryId);
            
            if (entryInfo.success) {
                return entryInfo;
            }
            attempts++;
        }
        throw new Error('Обработка не завершена');
    };

    const handleSubmit = async () => {
        const isValidLongitude = coords[0] >= -180 && coords[0] <= 180;
        const isValidLatitude = coords[1] >= -90 && coords[1] <= 90;

        if (!startDate || !endDate || !isValidLongitude || !isValidLatitude) {
            alert('Пожалуйста, заполните все поля корректно\nДолгота: -180 до 180\nШирота: -90 до 90');
            return;
        }

        setIsProcessing(true);
        setShowResult(false);

        try {
            const requestData = {
                start: new Date(startDate).toISOString(),
                end: new Date(endDate).toISOString(),
                coordinates: coords
            };

            const sentinelResponse = await fetch(backend_url + '/sentinel', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                },
                body: JSON.stringify(requestData)
            });

            if (!sentinelResponse.ok) throw new Error('Ошибка запуска обработки');
            
            const { entry_id } = await sentinelResponse.json();
            if (!entry_id) throw new Error('Не получен ID обработки');
            setEntryId(entry_id);

            const result = await processEntry(entry_id);

            setEntryData({
                source_url: result.source_url,
                sar_url: result.sar_url,
                result_url: result.result_url,
            });
            
            setShowResult(true);
        } catch (error) {
            console.error('Error:', error);
            alert(error.message);
        } finally {
            setIsProcessing(false);
        }
    };

    return (
        <section id="sentinel_hub">
            <div className="container">
                <h2 className="text-center mb-4">Обработка по координатам (Sentinel Hub)</h2>
                
                <div className="sentinel-inputs">
                    <div className="input-row">
                        <div className="input-group">
                            <label htmlFor="start-date">Начальная дата</label>
                            <input 
                                type="date" 
                                id="start-date" 
                                className="date-input"
                                value={startDate}
                                onChange={(e) => setStartDate(e.target.value)}
                            />
                        </div>
                        <div className="input-group">
                            <label htmlFor="end-date">Конечная дата</label>
                            <input 
                                type="date" 
                                id="end-date" 
                                className="date-input"
                                value={endDate}
                                onChange={(e) => setEndDate(e.target.value)}
                            />
                        </div>
                    </div>
                    
                    <div className="input-row">
                        {['Долгота', 'Широта'].map((label, index) => (
                            <div className="input-group" key={index}>
                                <label htmlFor={`coord${index+1}`}>{label}</label>
                                <input
                                    type="number"
                                    step="0.000001"
                                    id={`coord${index+1}`}
                                    className="coordinate-input"
                                    value={coords[index]}
                                    onChange={(e) => handleCoordChange(index, e.target.value)}
                                    placeholder={index === 0 ? "Напр. 37.6176" : "Напр. 55.7558"}
                                />
                            </div>
                        ))}
                    </div>
                </div>

                <div className="sentinel-images-container">
                    <div className="image-box">
                        <h3>Real</h3>
                        <div className="sentinel-image">
                            {entryData.source_url ? (
                                <img src={entryData.source_url} alt="Исходное изображение" />
                            ) : (
                                <p>Real</p>
                            )}
                        </div>
                    </div>
                    
                    <div className="image-box">
                        <h3>SAR</h3>
                        <div className="sentinel-image">
                            {entryData.sar_url ? (
                                <img src={entryData.sar_url} alt="SAR изображение" />
                            ) : (
                                <p>SAR</p>
                            )}
                        </div>
                    </div>
                    
                    <div className="image-box">
                        <h3>Result</h3>
                        <div className="sentinel-image">
                            {entryData.result_url ? (
                                <img src={entryData.result_url} alt="Результат обработки" />
                            ) : (
                                <p>Result</p>
                            )}
                        </div>
                    </div>
                </div>
                
                <div className="generate-btn-container">
                    <button 
                        className="generate-btn" 
                        onClick={handleSubmit}
                        disabled={isProcessing}
                    >
                        {isProcessing ? (
                            <>
                                <div className="spinner-border spinner-border-sm" role="status" style={{ marginRight: '8px' }}>
                                    <span className="visually-hidden">Loading...</span>
                                </div>
                                Обработка...
                            </>
                        ) : (
                            <>
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                                    <path d="M5.52.359A.5.5 0 0 1 6 0h4a.5.5 0 0 1 .474.658L8.694 6H12.5a.5.5 0 0 1 .395.807l-7 9a.5.5 0 0 1-.873-.454L6.823 9.5H3.5a.5.5 0 0 1-.48-.641l2.5-8.5z"/>
                                </svg>
                                Обработать изображение
                            </>
                        )}
                    </button>
                </div>
            </div>
            
            <div className="bottom-center">
                <button className="scroll-down" onClick={() => scrollHandler(4)}>▼</button>
            </div>
        </section>
    );
}