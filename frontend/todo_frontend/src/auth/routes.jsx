import React from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from './AuthContext';

const Splash = () => <div className="splash" role="status">Loading…</div>;

export const ProtectedRoute = () => {
  const { user, initializing } = useAuth();
  const location = useLocation();
  if (initializing) return <Splash />;
  return user ? <Outlet /> : <Navigate to="/login" replace state={{ from: location }} />;
};

export const PublicOnlyRoute = () => {
  const { user, initializing } = useAuth();
  if (initializing) return <Splash />;
  return user ? <Navigate to="/app" replace /> : <Outlet />;
};
