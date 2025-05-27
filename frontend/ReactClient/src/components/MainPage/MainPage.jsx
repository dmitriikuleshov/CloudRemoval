import { useRef, useEffect, useState } from 'react';

import '../../static/css/style1.css'
import { Navbar } from './Navbar'
import { Header } from './Header'
import { AboutSection } from './AboutSection'
import { ImageProcessingSection } from './ImageProcessingSection'
import { SarSection } from './SarSection'
import { LinksSection } from './LinksSection'
import { Footer } from './Footer'
import { useAuth } from '../context/AuthContext';

export function MainPage() {
    const { user, loading } = useAuth();
    useEffect(() => {
        if (loading)
            return;
    }, [user, loading]);
    const containerRef = useRef(null);
    const [sections, setSections] = useState([]);

    const scrollToSection = (index) => {
        setSections(containerRef.current.querySelectorAll('section'))
        if (sections[index]) {
            sections[index].scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    };

    useEffect(() => {
        if (containerRef.current) {
            const elements = containerRef.current.querySelectorAll('section');
            setSections(Array.from(elements));
        }
    }, []);

    return (
        <div ref={containerRef}>
            <Navbar />
            <Header scrollHandler={() => scrollToSection(0)} />
            <AboutSection scrollHandler={() => scrollToSection(1)} />
            <ImageProcessingSection scrollHandler={() => scrollToSection(2)} />
            <SarSection scrollHandler={() => scrollToSection(3)} />
            <LinksSection />
            <Footer />
        </div>
    )
}