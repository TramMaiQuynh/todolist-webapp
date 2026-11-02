import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { authApi } from '../api/resources';
import { setUnauthorizedHandler } from '../api/httpClient';
import { tokenStorage } from '../api/tokenStorage';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  // Đang kiểm tra token đã lưu hay chưa (tránh nháy trang đăng nhập)
  const [initializing, setInitializing] = useState(() => Boolean(tokenStorage.get()));

  const clearSession = useCallback(() => {
    tokenStorage.clear();
    setUser(null);
  }, []);

  useEffect(() => {
    setUnauthorizedHandler(clearSession);
  }, [clearSession]);

  useEffect(() => {
    if (!tokenStorage.get()) return;
    authApi
      .me()
      .then(setUser)
      .catch(clearSession)
      .finally(() => setInitializing(false));
  }, [clearSession]);

  const startSession = useCallback(({ token, user: nextUser }) => {
    tokenStorage.set(token);
    setUser(nextUser);
  }, []);

  const login = useCallback(
    async (credentials) => startSession(await authApi.login(credentials)),
    [startSession]
  );

  const register = useCallback(
    async (payload) => startSession(await authApi.register(payload)),
    [startSession]
  );

  const logout = useCallback(async () => {
    try {
      await authApi.logout();
    } catch {
      /* token có thể đã hết hạn: vẫn đăng xuất phía client */
    }
    clearSession();
  }, [clearSession]);

  const value = useMemo(
    () => ({ user, initializing, login, register, logout }),
    [user, initializing, login, register, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used inside <AuthProvider>');
  return context;
};
