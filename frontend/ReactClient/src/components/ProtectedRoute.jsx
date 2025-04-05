import { Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';

export const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return <div>Loading...</div>;
  }


  return children;
};