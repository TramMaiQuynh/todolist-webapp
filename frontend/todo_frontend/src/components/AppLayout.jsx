import React from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import Brand from './Brand';

const AppLayout = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const signOut = async () => {
    await logout();
    navigate('/login', { replace: true });
  };

  return (
    <>
      <header className="topbar">
        <NavLink to="/app" className="brand-link" aria-label="Daymark home"><Brand /></NavLink>
        <nav className="primary-nav" aria-label="Main">
          <NavLink to="/app">My tasks</NavLink>
          <NavLink to="/insights">Activity</NavLink>
        </nav>
        <div className="user">
          <span className="user-avatar" aria-hidden="true">{user.username?.slice(0, 1).toUpperCase()}</span>
          <span className="user-name">{user.username}</span>
          <button type="button" className="btn ghost sign-out" onClick={signOut}>Sign out</button>
        </div>
      </header>
      <Outlet />
    </>
  );
};

export default AppLayout;
