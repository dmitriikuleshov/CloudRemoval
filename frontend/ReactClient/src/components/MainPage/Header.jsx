import background from '../../static/videos/background.mp4'
import '../../static/css/style1.css'
export function Header({scrollHandler}) {
    return (
        <header>
        <video autoPlay muted loop id="bg-video">
            <source src={background} type="video/mp4" />
            Ваш браузер не поддерживает видео.
        </video>
        <h1>Удаление Облаков</h1>
        <div className="bottom-center">
            <button className="scroll-down" onClick={scrollHandler}>▼</button>
        </div>
        </header>
    )}
// Add scroll scripts