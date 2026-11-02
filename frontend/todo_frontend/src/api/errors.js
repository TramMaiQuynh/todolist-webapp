const flatten = (value) => (Array.isArray(value) ? value.join(' ') : String(value));

/** Lỗi theo trường từ DRF: { title: "…", due_date: "…" } (rỗng nếu không có). */
export const fieldErrors = (error) => {
  const data = error?.response?.data;
  if (!data || typeof data !== 'object' || Array.isArray(data)) return {};
  return Object.fromEntries(
    Object.entries(data)
      .filter(([key]) => key !== 'detail')
      .map(([key, value]) => [key, flatten(value)])
  );
};

/** Thông điệp thân thiện duy nhất cho toast. */
export const errorMessage = (error, fallback = 'Something went wrong. Please try again.') => {
  if (!error?.response) {
    return error?.code === 'ECONNABORTED'
      ? 'The server took too long to respond.'
      : 'Cannot reach the server. Check your connection.';
  }
  const { status, data } = error.response;
  if (status === 429) return 'Too many requests. Please wait a moment.';
  if (status >= 500) return 'Server error. Please try again later.';
  if (data?.detail) return flatten(data.detail);
  const fields = Object.entries(fieldErrors(error));
  if (fields.length) {
    return fields.map(([key, msg]) => `${key.replace(/_/g, ' ')}: ${msg}`).join(' · ');
  }
  return fallback;
};
