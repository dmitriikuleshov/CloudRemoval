import { Link } from "react-router-dom";
import { useAuth } from '../context/AuthContext';
import '../../static/css/auth.css';
import '../../static/css/profile.css'
import background from '../../static/videos/1479.gif'
import { Footer } from '../MainPage/Footer';
export function ProfilePage() {
    const {user, loading, logout} = useAuth();
    
    if (loading) {
        return <div>Загрузка...</div>;
    }

    if (!user) {
        return <div>Пользователь не авторизован</div>;
    }
    return (
        <>
    <div style={{background: `url(${background}) center/cover no-repeat fixed`, position: 'relative', height: '72.1vh'}}>
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
        </div>

    </div>
    <Footer id="contact"/>
    </>
    )
}