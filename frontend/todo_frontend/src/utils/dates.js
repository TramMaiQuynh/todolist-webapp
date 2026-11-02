// due_date là chuỗi "YYYY-MM-DD" (không có múi giờ). Không dùng new Date(str) vì sẽ
// bị lệch ngày theo múi giờ; tách chuỗi để hiển thị đúng ngày server trả về.

export const formatDate = (iso) => {
  if (!iso) return '';
  const [year, month, day] = iso.slice(0, 10).split('-');
  return `${day}/${month}/${year}`;
};

export const formatDateTime = (iso) => (iso ? new Date(iso).toLocaleString() : '');

export const formatMinutes = (minutes) => {
  if (minutes == null) return '';
  const hours = Math.floor(minutes / 60);
  const rest = minutes % 60;
  if (!hours) return `${rest}m`;
  return rest ? `${hours}h ${rest}m` : `${hours}h`;
};
