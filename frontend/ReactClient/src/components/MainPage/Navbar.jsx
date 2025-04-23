import { Link, useNavigate } from "react-router-dom";
import project_logo from "./img/project_logo.jpg";
import { useAuth } from "../context/AuthContext";

export function Navbar() {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
    };

    return (
        <nav className="navbar navbar-expand-lg fixed-top">
            <div className="container">
                <Link className="navbar-brand" to="/">
                    <img src={project_logo} alt="Logo" className="logo-image" />
                </Link>
                <div className="brand-title" style={user ? { left: '28%'} : { left: '50%'}}>
                    УДАЛЕНИЕ ОБЛАКОВ BY ГАЛЕРА
                </div>
                

                <ul className="navbar-nav ms-auto">
                    <li className="nav-item">
                        <Link className="nav-link active" to="/">Главная</Link>
                    </li>
                    

                    <li className="nav-item dropdown">
                            <button 
                                className="nav-link dropdown-toggle" 
                                id="navbarDropdown" 
                                data-bs-toggle="dropdown" 
                                aria-expanded="false"
                            >
                                Меню
                            </button>
                            <ul className="dropdown-menu" aria-labelledby="navbarDropdown">
                                <li><a className="dropdown-item" href="#description">О проекте</a></li>
                                <li><a className="dropdown-item" href="#image_processing">Обработка изображений</a></li>
                                <li><a className="dropdown-item" href="#links">Полезные ссылки</a></li>
                            </ul>
                        </li>
                        <li className="nav-item">
                            <a className="nav-link" href="#contact">Контакты</a>
                        </li>

                    {user ? (
                        <>
                            <li className="nav-item">
                                <Link className="nav-link text-primary" to="/profile">{user.username}</Link>
                            </li>
                            <li className="nav-item">
                                <button 
                                    onClick={handleLogout} 
                                    className="btn btn-link nav-link text-danger"
                                >
                                    Выйти
                                </button>
                            </li>
                        </>
                    ) : (
                        <li className="nav-item">
                            <button
                                className="login-btn"
                                onClick={() => navigate("/login")}
                                style={{border: 'none'}}
                            >
                                Войти
                            </button>
                        </li>
                    )}
                </ul>
            </div>
        </nav>
    )
}