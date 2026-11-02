import { useCallback, useEffect, useState } from 'react';
import { categoriesApi, tagsApi, tasksApi } from '../api/resources';
import { errorMessage } from '../api/errors';

const FALLBACK_META = {
  statuses: [],
  priorities: [],
  recurrences: [],
  bulk_actions: [],
};

// Các danh sách tra cứu có thể phân trang: lấy lớn một lần là đủ cho dropdown.
const LOOKUP_PARAMS = { page_size: 100 };

/** Danh mục, thẻ và metadata (giá trị hợp lệ do server cung cấp) cho form/bộ lọc. */
export const useLookups = () => {
  const [categories, setCategories] = useState([]);
  const [tags, setTags] = useState([]);
  const [meta, setMeta] = useState(FALLBACK_META);
  const [error, setError] = useState('');

  const refresh = useCallback(async () => {
    try {
      const [cats, tagList, metaData] = await Promise.all([
        categoriesApi.list(LOOKUP_PARAMS),
        tagsApi.list(LOOKUP_PARAMS),
        tasksApi.meta(),
      ]);
      setCategories(cats.results);
      setTags(tagList.results);
      setMeta(metaData);
      setError('');
    } catch (err) {
      setError(errorMessage(err, 'Could not load categories and tags.'));
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const createCategory = useCallback(async (name) => {
    const created = await categoriesApi.create({ name });
    setCategories((prev) => [...prev, created].sort((a, b) => a.name.localeCompare(b.name)));
    return created;
  }, []);

  const createTag = useCallback(async (name) => {
    const created = await tagsApi.create({ name });
    setTags((prev) => [...prev, created].sort((a, b) => a.name.localeCompare(b.name)));
    return created;
  }, []);

  return { categories, tags, meta, error, refresh, createCategory, createTag };
};
