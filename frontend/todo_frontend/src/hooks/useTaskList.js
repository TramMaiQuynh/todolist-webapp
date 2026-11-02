import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { tasksApi } from '../api/resources';
import { errorMessage } from '../api/errors';
import { PAGE_SIZE } from '../config';
import { useDebouncedValue } from './useDebouncedValue';

export const DEFAULT_FILTERS = {
  search: '',
  status: '',
  priority: '',
  category: '',
  tag: '',
  due: '',          // '' | 'overdue' | 'today'
  important: false,
  archived: 'false',
  ordering: '-created_at',
};

/** Chuyển state bộ lọc của UI thành query params của API. Thêm bộ lọc = thêm 1 dòng ở đây. */
const toParams = (filters, page) => {
  const params = { page, page_size: PAGE_SIZE, ordering: filters.ordering, archived: filters.archived };
  if (filters.search.trim()) params.search = filters.search.trim();
  if (filters.status) params.status = filters.status;
  if (filters.priority) params.priority = filters.priority;
  if (filters.category) params.category = filters.category;
  if (filters.tag) params.tags = filters.tag;
  if (filters.important) params.is_important = true;
  if (filters.due === 'overdue') params.overdue = true;
  if (filters.due === 'today') params.due_today = true;
  params.top_level = true; // task con hiển thị bên trong task cha
  return params;
};

export const useTaskList = () => {
  const [filters, setFiltersState] = useState(DEFAULT_FILTERS);
  const [page, setPage] = useState(1);
  const [data, setData] = useState({ results: [], count: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const requestId = useRef(0);

  const debouncedSearch = useDebouncedValue(filters.search);
  const effective = useMemo(() => ({ ...filters, search: debouncedSearch }), [filters, debouncedSearch]);

  const load = useCallback(async () => {
    const id = ++requestId.current; // bỏ qua phản hồi cũ đến muộn
    setLoading(true);
    try {
      const result = await tasksApi.list(toParams(effective, page));
      if (id !== requestId.current) return;
      if (result.results.length === 0 && page > 1) {
        setPage(page - 1); // trang hiện tại vừa hết dữ liệu (ví dụ sau khi xóa)
        return;
      }
      setData(result);
      setError('');
    } catch (err) {
      if (id !== requestId.current) return;
      setError(errorMessage(err, 'Could not load tasks.'));
    } finally {
      if (id === requestId.current) setLoading(false);
    }
  }, [effective, page]);

  useEffect(() => {
    load();
  }, [load]);

  const setFilters = useCallback((patch) => {
    setFiltersState((prev) => ({ ...prev, ...patch }));
    setPage(1);
  }, []);

  const resetFilters = useCallback(() => {
    setFiltersState(DEFAULT_FILTERS);
    setPage(1);
  }, []);

  const hasActiveFilters = useMemo(
    () => Object.keys(DEFAULT_FILTERS).some((k) => k !== 'ordering' && filters[k] !== DEFAULT_FILTERS[k]),
    [filters]
  );

  return {
    tasks: data.results,
    count: data.count,
    page,
    pageCount: Math.max(1, Math.ceil(data.count / PAGE_SIZE)),
    setPage,
    filters,
    setFilters,
    resetFilters,
    hasActiveFilters,
    loading,
    error,
    reload: load,
  };
};
