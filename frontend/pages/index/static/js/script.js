let isScrolling = false;
let currentSectionIndex = 0;
const sections = document.querySelectorAll('section, header');
const scrollDelay = 1200;


function scrollToSection(index) {
    if (index >= 0 && index < sections.length) {
        isScrolling = true;
        sections[index].scrollIntoView({ behavior: 'smooth' });

        // setTimeout(() => {
        //     isScrolling = false;
        // }, scrollDelay);
    }
}


window.addEventListener('wheel', (event) => {
    if (isScrolling) return;

    if (event.deltaY > 0) {
        currentSectionIndex = Math.min(currentSectionIndex + 1, sections.length - 1);
    } else {
        currentSectionIndex = Math.max(currentSectionIndex - 1, 0);
    }

    scrollToSection(currentSectionIndex);
});


// const video = document.getElementById('bg-video');
// video.play();

// if (pauseButton) {
//     pauseButton.addEventListener('click', function() {
//         if (video.paused) {
//             video.play();
//             pauseButton.textContent = 'Pause';
//         } else {
//             video.pause();
//             pauseButton.textContent = 'Play';
//         }
//     });
// }

// Функционал обработки изображений
document.addEventListener('DOMContentLoaded', function() {
    const generateBtn = document.getElementById('generate-btn');
    const fileInput = document.getElementById('file-input');
    const resultPlaceholder = document.querySelector('.result-placeholder');
    const processingIndicator = document.querySelector('.processing-indicator');
    const processedResult = document.querySelector('.processed-result');
    const actionButtons = document.querySelector('.action-buttons');
    const processedImage = document.getElementById('processed-image');
    
    let uploadedImage = null;
    
    // Обработка загрузки файла
    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(event) {
                uploadedImage = event.target.result;
                // Показываем, что файл был загружен
                document.querySelector('.file-input-label').textContent = file.name;
            };
            reader.readAsDataURL(file);
        }
    });
    
    // Обработка нажатия на кнопку Generate
    generateBtn.addEventListener('click', function() {
        if (!uploadedImage) {
            alert('Пожалуйста, сначала загрузите изображение');
            return;
        }
        
        // Скрываем текст-заполнитель
        resultPlaceholder.style.display = 'none';
        
        // Показываем индикатор загрузки
        processingIndicator.style.display = 'block';
        processedResult.style.display = 'none';
        actionButtons.style.display = 'none';
        
        // Имитируем процесс обработки
        setTimeout(function() {
            // Скрываем индикатор загрузки
            processingIndicator.style.display = 'none';
            
            // Показываем результат (в данном случае просто используем загруженное изображение)
            processedImage.src = uploadedImage;
            processedResult.style.display = 'block';
            
            // Показываем кнопки действий
            actionButtons.style.display = 'flex';
        }, 3000); // Имитация 3-секундной обработки
    });
    
    // Обработка нажатия на кнопку "Лайк"
    document.querySelector('.like-btn').addEventListener('click', function() {
        alert('Спасибо за оценку! Результат сохранён.');
    });
    
    // Обработка нажатия на кнопку "Обработать заново"
    document.querySelector('.reprocess-btn').addEventListener('click', function() {
        // Скрываем результат и кнопки
        processedResult.style.display = 'none';
        actionButtons.style.display = 'none';
        
        // Показываем индикатор загрузки
        processingIndicator.style.display = 'block';
        
        // Имитируем повторную обработку
        setTimeout(function() {
            // Скрываем индикатор загрузки
            processingIndicator.style.display = 'none';
            
            // Показываем результат и кнопки действий
            processedResult.style.display = 'block';
            actionButtons.style.display = 'flex';
        }, 2000); // Имитация 2-секундной повторной обработки
    });
});

// Плавная прокрутка для внутренних ссылок в навигации
document.addEventListener('DOMContentLoaded', function() {
    // Выбираем все ссылки в навигации и dropdown меню
    const navLinks = document.querySelectorAll('.navbar-nav a.nav-link, .dropdown-menu a.dropdown-item');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Проверяем, является ли ссылка внутренней (начинается с #)
            const href = this.getAttribute('href');
            if (href.startsWith('#') && href.length > 1) {
                e.preventDefault();
                
                const targetId = href.substring(1);
                const targetSection = document.getElementById(targetId);
                
                if (targetSection) {
                    // Плавная прокрутка к секции
                    targetSection.scrollIntoView({ 
                        behavior: 'smooth',
                        block: 'start'
                    });
                    
                    // Если на мобильном устройстве, закрываем меню
                    const navbarCollapse = document.querySelector('.navbar-collapse');
                    if (navbarCollapse.classList.contains('show')) {
                        const bsCollapse = new bootstrap.Collapse(navbarCollapse);
                        bsCollapse.hide();
                    }
                }
            }
        });
    });
});

// Изменение стиля навбара при прокрутке
document.addEventListener('DOMContentLoaded', function() {
    const navbar = document.querySelector('.navbar');
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
});

// Обработка клика по ссылке "Контакты"
document.addEventListener('DOMContentLoaded', function() {
    const contactLink = document.querySelector('a[href="#contact"]');
    
    contactLink.addEventListener('click', function(e) {
        e.preventDefault();
        
        const footer = document.getElementById('contact');
        footer.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
        
        // Закрываем меню на мобильных устройствах
        const navbarCollapse = document.querySelector('.navbar-collapse');
        if (navbarCollapse.classList.contains('show')) {
            const bsCollapse = new bootstrap.Collapse(navbarCollapse);
            bsCollapse.hide();
        }
    });
});
