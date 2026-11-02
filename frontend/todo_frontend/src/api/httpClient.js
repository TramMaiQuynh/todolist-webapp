import axios from 'axios';
import { API_BASE_URL } from '../config';
import { tokenStorage } from './tokenStorage';

export const http = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
});

http.interceptors.request.use((config) => {
  const token = tokenStorage.get();
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

// AuthContext đăng ký callback này để xử lý phiên hết hạn ở một chỗ duy nhất.
let onUnauthorized = () => {};
export const setUnauthorizedHandler = (handler) => {
  onUnauthorized = handler;
};

const PUBLIC_PATHS = ['/auth/login/', '/auth/register/'];

http.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status;
    const url = error.config?.url || '';
    if (status === 401 && !PUBLIC_PATHS.includes(url)) {
      onUnauthorized();
    }
    return Promise.reject(error);
  }
);
