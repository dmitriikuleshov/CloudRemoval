import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthPage } from './components/AuthPage/AuthPage';
import { MainPage } from './components/MainPage/MainPage';
import { AuthProvider } from './components/context/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { ProfilePage } from './components/ProfilePage/ProfilePage';
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
          <Route
            path='/profile'
            element={
              <ProtectedRoute>
                <ProfilePage />
              </ProtectedRoute>
            }
          />
        </Routes>
      </AuthProvider>
    </Router>
  );
}