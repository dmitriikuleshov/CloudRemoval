import background from '../../static/videos/1479.gif'
import '../../static/css/style1.css'
export function Header({scrollHandler}) {
    return (
        <header id="header">
        <img src={background} alt="Фоновая анимация" id="bg-gif"/>
        <h1>Удаление Облаков</h1>
        <div className="bottom-center">
            <button className="scroll-down" onClick={scrollHandler}>▼</button>
        </div>
        </header>
    )}
// Add scroll scripts