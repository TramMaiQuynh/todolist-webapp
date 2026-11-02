// Nhãn hiển thị cho các giá trị enum của backend. Giá trị lạ vẫn hiển thị được (fallback).
const STATUS_LABELS = {
  Pending: 'Pending',
  In_progress: 'In progress',
  Completed: 'Completed',
};

export const statusLabel = (status) => STATUS_LABELS[status] || status;

export const recurrenceLabel = (frequency, interval) => {
  if (!frequency) return '';
  return interval > 1 ? `Every ${interval} × ${frequency}` : `Repeats ${frequency}`;
};
