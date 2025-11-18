/** Private route component to protect authenticated routes. */
import React from 'react';
import { Navigate } from 'react-router-dom';
import { authApi } from '../services/api';

interface PrivateRouteProps {
  children: React.ReactNode;
}

export const PrivateRoute: React.FC<PrivateRouteProps> = ({ children }) => {
  const token = authApi.getToken();
  const user = authApi.getUser();

  if (!token || !user) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

