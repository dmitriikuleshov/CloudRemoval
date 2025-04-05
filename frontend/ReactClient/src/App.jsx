import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthPage } from './components/AuthPage/AuthPage';
import { MainPage } from './components/MainPage/MainPage';
import { AuthProvider } from './components/context/AuthContext';

export function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<AuthPage />} />
          <Route
            path="/"
            element={
                <MainPage />
            }
          />
        </Routes>
      </AuthProvider>
    </Router>
  );
}