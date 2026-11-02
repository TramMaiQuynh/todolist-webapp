import { http } from './httpClient';

const data = (promise) => promise.then((response) => response.data);

/** Factory CRUD dùng chung cho mọi tài nguyên REST (DRY, mở rộng không sửa code cũ). */
export const createResource = (path) => ({
  list: (params) => data(http.get(`/${path}/`, { params })),
  get: (id) => data(http.get(`/${path}/${id}/`)),
  create: (payload) => data(http.post(`/${path}/`, payload)),
  update: (id, payload) => data(http.patch(`/${path}/${id}/`, payload)),
  remove: (id) => http.delete(`/${path}/${id}/`),
});

export const categoriesApi = createResource('categories');
export const tagsApi = createResource('tags');

const tasksResource = createResource('tasks');

export const tasksApi = {
  ...tasksResource,
  changeStatus: (id, status) => data(http.post(`/tasks/${id}/change_status/`, { status })),
  archive: (id) => data(http.post(`/tasks/${id}/archive/`)),
  restore: (id) => data(http.post(`/tasks/${id}/restore/`)),
  bulk: (payload) => data(http.post('/tasks/bulk/', payload)),
  statistics: (days = 30) => data(http.get('/tasks/statistics/', { params: { days } })),
  meta: () => data(http.get('/tasks/meta/')),
};

export const authApi = {
  register: (payload) => data(http.post('/auth/register/', payload)),
  login: (payload) => data(http.post('/auth/login/', payload)),
  logout: () => http.post('/auth/logout/'),
  me: () => data(http.get('/auth/me/')),
};
