import React from 'react';
import { BrowserRouter as Router, Link, Route, Routes } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { AuthProvider } from './auth/AuthContext';
import { ProtectedRoute, PublicOnlyRoute } from './auth/routes';
import AppLayout from './components/AppLayout';
import Footer from './components/Footer';
import AppPage from './pages/AppPage';
import AuthPage from './pages/AuthPage';
import HomePage from './pages/HomePage';
import StatsPage from './pages/StatsPage';
import './index.css';
import './styles/app.css';

const NotFound = () => (
  <main className="page empty">
    <h1>Page not found</h1>
    <p><Link to="/">Back to home</Link></p>
  </main>
);

const App = () => (
  <Router>
    <AuthProvider>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route element={<PublicOnlyRoute />}>
          <Route path="/login" element={<AuthPage mode="login" />} />
          <Route path="/register" element={<AuthPage mode="register" />} />
        </Route>
        <Route element={<ProtectedRoute />}>
          <Route element={<AppLayout />}>
            <Route path="/app" element={<AppPage />} />
            <Route path="/insights" element={<StatsPage />} />
          </Route>
        </Route>
        <Route path="*" element={<NotFound />} />
      </Routes>
      <Footer />
      <ToastContainer position="top-right" autoClose={3500} />
    </AuthProvider>
  </Router>
);

export default App;
