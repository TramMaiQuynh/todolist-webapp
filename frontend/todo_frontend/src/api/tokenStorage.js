const KEY = 'todo.token';

// localStorage có thể bị chặn (chế độ riêng tư...), nên mọi truy cập đều bọc try/catch.
export const tokenStorage = {
  get() {
    try {
      return window.localStorage.getItem(KEY);
    } catch {
      return null;
    }
  },
  set(token) {
    try {
      window.localStorage.setItem(KEY, token);
    } catch {
      /* bỏ qua */
    }
  },
  clear() {
    try {
      window.localStorage.removeItem(KEY);
    } catch {
      /* bỏ qua */
    }
  },
};
