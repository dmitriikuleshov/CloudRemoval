import { Link } from "react-router-dom";
import { useAuth } from '../context/AuthContext';
import '../../static/css/auth.css';
import '../../static/css/profile.css'
import background from '../../static/videos/1479.gif'

export function ProfilePage() {
    const {user, loading, logout} = useAuth();
    
    if (loading) {
        return <div>Загрузка...</div>;
    }

    if (!user) {
        return <div>Пользователь не авторизован</div>;
    }
    return (
    <div style={{background: `url(${background}) center/cover no-repeat fixed`, position: 'relative'}}>
    <div className="profile-header">
        <div className="header-left">
            <Link to="/" className="back-to-home">
                <svg className="house-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                    <path d="M12 2L2 12h3v8h6v-6h2v6h6v-8h3L12 2zm0 2.828L18.172 10H16v8h-2v-6H10v6H8v-8H5.828L12 4.828z"/>
                </svg>
                Вернуться на главную
            </Link>
        </div>
        <div className="header-right">
            <button onClick={logout} className="logout-btn">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                    <path fillRule="evenodd" d="M10 12.5a.5.5 0 0 1-.5.5h-8a.5.5 0 0 1-.5-.5v-9a.5.5 0 0 1 .5-.5h8a.5.5 0 0 1 .5.5v2a.5.5 0 0 0 1 0v-2A1.5 1.5 0 0 0 9.5 2h-8A1.5 1.5 0 0 0 0 3.5v9A1.5 1.5 0 0 0 1.5 14h8a1.5 1.5 0 0 0 1.5-1.5v-2a.5.5 0 0 0-1 0v2z"/>
                    <path fillRule="evenodd" d="M15.854 8.354a.5.5 0 0 0 0-.708l-3-3a.5.5 0 0 0-.708.708L14.293 7.5H5.5a.5.5 0 0 0 0 1h8.793l-2.147 2.146a.5.5 0 0 0 .708.708l3-3z"/>
                </svg>
                Выйти
            </button>
        </div>
    </div>

    <div className="profile-container">
        <div className="personal-info">
            <h2>Личная информация</h2>
            <div className="info-item">
                <span className="info-label">Имя пользователя</span>
                <span className="info-value" id="username">{user.username}</span>
            </div>
            <div className="info-item">
                <span className="info-label">Имя</span>
                <span className="info-value" id="name">{user.name}</span>
            </div>
            <div className="info-item">
                <span className="info-label">Фамилия</span>
                <span className="info-value" id="surname">{user.surname}</span>
            </div>
            <div className="info-item">
                <span className="info-label">Email</span>
                <span className="info-value" id="email">{user.email}</span>
            </div>
        </div>

        <div className="gallery-buttons">
            <button className="gallery-btn active" onClick="showGallery('liked')">Понравившиеся фото</button>
        </div>

        <div id="liked-gallery" className="gallery active">
            {/* <!-- Понравившиеся фото будут добавляться сюда --> */}
        </div>

        {/* <!-- Добавляем панель действий с фото --> */}
        <div className="gallery-actions">
            <button className="action-btn download-btn" onClick="startPhotoSelection('download')">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor">
                    <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>
                    <path d="M8 4a.5.5 0 0 1 .5.5v5.793l2.146-2.147a.5.5 0 0 1 .708.708l-3 3a.5.5 0 0 1-.708 0l-3-3a.5.5 0 1 1 .708-.708L7.5 10.293V4.5A.5.5 0 0 1 8 4z"/>
                </svg>
                Скачать фотографии
            </button>
            <button className="action-btn delete-btn" onClick="startPhotoSelection('delete')">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor">
                    <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/>
                    <path fillRule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/>
                </svg>
                Удалить фотографии
            </button>
        </div>

        {/* <!-- Обновляем счетчик выбранных фото --> */}
        <div className="selection-count" id="selectionCount">
            <span>Выбрано: <span id="selectedCount">0</span></span>
            <button className="confirm-selection" id="confirmSelection" style={{display: "none"}}>
                <span id="confirmSelectionText">Подтвердить</span>
            </button>
            <button className="cancel-selection" onClick="cancelSelection()">Отмена</button>
        </div>
    </div>

    {/* <!-- Обновляем модальное окно для просмотра фото --> */}
    <div className="photo-modal" id="photoModal">
        <div className="modal-content">
            <div className="modal-side left" onClick="closePhotoModal()"></div>
            <div className="modal-image-container" onClick="event.stopPropagation()">
                <img src="" alt="Фото в полном размере" className="modal-image" id="modalImage"/>
            </div>
            <div className="modal-side right" onClick="closePhotoModal()"></div>
            <div className="modal-nav" onClick="event.stopPropagation()">
                <button onClick="showPreviousPhoto()" id="prevPhotoBtn">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor">
                        <path fillRule="evenodd" d="M11.354 1.646a.5.5 0 0 1 0 .708L5.707 8l5.647 5.646a.5.5 0 0 1-.708.708l-6-6a.5.5 0 0 1 0-.708l6-6a.5.5 0 0 1 .708 0z"/>
                    </svg>
                </button>
                <button onClick="showNextPhoto()" id="nextPhotoBtn">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor">
                        <path fillRule="evenodd" d="M4.646 1.646a.5.5 0 0 1 .708 0l6 6a.5.5 0 0 1 0 .708l-6 6a.5.5 0 0 1-.708-.708L10.293 8 4.646 2.354a.5.5 0 0 1 0-.708z"/>
                    </svg>
                </button>
            </div>
        </div>
    </div>

    <footer id="contact">
        <div className="container">
            <h3>Галера</h3>
            <p className="footer-text">...</p>
            <div className="footer-contacts">
                <a><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" className="bi bi-telephone" viewBox="0 0 16 16">
                    <path d="M3.654 1.328a.678.678 0 0 0-1.015-.063L1.605 2.3c-.483.484-.661 1.169-.45 1.77a17.6 17.6 0 0 0 4.168 6.608 17.6 17.6 0 0 0 6.608 4.168c.601.211 1.286.033 1.77-.45l1.034-1.034a.678.678 0 0 0-.063-1.015l-2.307-1.794a.68.68 0 0 0-.58-.122l-2.19.547a1.75 1.75 0 0 1-1.657-.459L5.482 8.062a1.75 1.75 0 0 1-.46-1.657l.548-2.19a.68.68 0 0 0-.122-.58zM1.884.511a1.745 1.745 0 0 1 2.612.163L6.29 2.98c.329.423.445.974.315 1.494l-.547 2.19a.5.5 0 0 0 .178.643l2.457 2.457a.5.5 0 0 0 .644.178l2.189-.547a1.75 1.75 0 0 1 1.494.315l2.306 1.794c.829.645.905 1.87.163 2.611l-1.034 1.034c-.74.74-1.846 1.065-2.877.702a18.6 18.6 0 0 1-7.01-4.42 18.6 18.6 0 0 1-4.42-7.009c-.362-1.03-.037-2.137.703-2.877z"/>
                </svg> +79999999999 
                </a>
                <a>
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" className="bi bi-envelope" viewBox="0 0 16 16">
                    <path d="M0 4a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2zm2-1a1 1 0 0 0-1 1v.217l7 4.2 7-4.2V4a1 1 0 0 0-1-1zm13 2.383-4.708 2.825L15 11.105zm-.034 6.876-5.64-3.471L8 9.583l-1.326-.795-5.64 3.47A1 1 0 0 0 2 13h12a1 1 0 0 0 .966-.741M1 11.105l4.708-2.897L1 5.383z"/>
                </svg> support@cloudclear.ru
                </a>
            </div>
        </div>
        <div className="container">
            <h3>Наши социальные сети</h3>
            <div className="social-links">
                <a href="#" className="social-link" title="ВКонтакте">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M15.684 0H8.316C1.592 0 0 1.592 0 8.316v7.368C0 22.408 1.592 24 8.316 24h7.368C22.408 24 24 22.408 24 15.684V8.316C24 1.592 22.391 0 15.684 0zm3.692 16.611h-1.729c-.583 0-.775-.128-1.12-.485-.347-.358-1.289-1.289-1.775-1.612-.336-.224-.368-.128-.368.224v1.353c0 .336-.112.52-.52.52h-.893c-1.009 0-2.221-.055-3.358-1.307-1.542-1.656-2.996-4.547-2.996-4.974 0-.183.111-.336.447-.336h1.716c.459 0 .571.235.694.583.571 1.68 1.586 3.149 2.01 3.149.173 0 .235-.084.235-.55v-1.903c-.054-.888-.505-1.01-.505-1.345 0-.173.137-.336.359-.336h2.657c.347 0 .459.168.459.571v2.552c0 .296.122.392.223.392.173 0 .324-.095.627-.392 1.009-1.137 1.716-2.873 1.716-2.873.097-.2.292-.381.662-.381h1.716c.492 0 .604.264.492.571-.207.961-2.191 3.724-2.191 3.724-.173.291-.235.403 0 .682.175.209.748.771 1.137 1.227.694.784 1.196 1.465 1.329 1.923.145.47-.097.706-.547.706z"/>
                    </svg>
                </a>
                <a href="#" className="social-link" title="Telegram">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/>
                    </svg>
                </a>
                <a href="#" className="social-link" title="X (Twitter)">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                        <path d="M12.6.75h2.454l-5.36 6.142L16 15.25h-4.937l-3.867-5.07-4.425 5.07H.316l5.733-6.57L0 .75h5.063l3.495 4.633L12.601.75Zm-.86 13.028h1.36L4.323 2.145H2.865z"/>
                    </svg>
                </a>
                <a href="#" className="social-link" title="GitHub">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                        <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.23.48-2.69-1.08-2.69-1.08-.36-.92-.89-1.17-.89-1.17-.73-.5.05-.49.05-.49.8.06 1.23.82 1.23.82.72 1.21 1.88.86 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.65-.89-3.65-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8z"/>
                    </svg>
                </a>
            </div>
        </div>
        <div className="container">
            <h3>Свяжитесь с нами</h3>
            <form className="contact-us" action="#" method="post">
                <input className="email-input" type="text" name="email" placeholder="Ваш email" required/><br/>
                <textarea className="message-input" name="message" placeholder="Ваше сообщение" required></textarea><br/>
                <button className="submit-button" type="submit"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" className="bi bi-send" viewBox="0 0 16 16">
                    <path d="M15.854.146a.5.5 0 0 1 .11.54l-5.819 14.547a.75.75 0 0 1-1.329.124l-3.178-4.995L.643 7.184a.75.75 0 0 1 .124-1.33L15.314.037a.5.5 0 0 1 .54.11ZM6.636 10.07l2.761 4.338L14.13 2.576zm6.787-8.201L1.591 6.602l4.339 2.76z"/>
                </svg> Отправить</button>
            </form>
        </div>
    </footer>
    </div>
    )
}