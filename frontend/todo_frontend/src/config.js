// Mặc định dùng cùng origin; đặt VITE_API_URL nếu API nằm ở domain khác.
export const API_BASE_URL = (import.meta.env.VITE_API_URL || '/api/v1').replace(/\/$/, '');

export const PAGE_SIZE = 20;
