import React, { useCallback, useEffect, useState } from 'react';
import { toast } from 'react-toastify';
import { tasksApi } from '../api/resources';
import BulkBar from '../components/BulkBar';
import Modal from '../components/Modal';
import Pagination from '../components/Pagination';
import TaskFilters from '../components/TaskFilters';
import TaskForm from '../components/TaskForm';
import TaskItem from '../components/TaskItem';
import { useLookups } from '../hooks/useLookups';
import { useTaskList } from '../hooks/useTaskList';

const AppPage = () => {
  const list = useTaskList();
  const lookups = useLookups();
  const [editing, setEditing] = useState(null);   // null | 'new' | task
  const [selected, setSelected] = useState([]);

  // Chuyển trang / đổi bộ lọc thì bỏ chọn để tránh thao tác nhầm lên task đang ẩn
  useEffect(() => {
    setSelected([]);
  }, [list.page, list.filters]);

  const refresh = useCallback(() => {
    list.reload();
    lookups.refresh();
  }, [list, lookups]);

  const closeForm = useCallback(() => setEditing(null), []);

  const save = async (payload) => {
    if (editing === 'new') {
      await tasksApi.create(payload);
      toast.success('Task created');
    } else {
      await tasksApi.update(editing.id, payload);
      toast.success('Task updated');
    }
    setEditing(null);
    refresh();
  };

  const toggleSelect = (id) =>
    setSelected((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]));

  const allSelected = list.tasks.length > 0 && selected.length === list.tasks.length;
  const today = new Intl.DateTimeFormat(undefined, {
    weekday: 'long', month: 'long', day: 'numeric',
  }).format(new Date());

  return (
    <main className="page task-page">
      <header className="task-page-heading">
        <div>
          <p className="eyebrow page-eyebrow"><span className="eyebrow-dot" /> {today}</p>
          <h1>My tasks<span className="heading-period">.</span></h1>
          <p className="page-subtitle">Keep your attention on what matters today.</p>
        </div>
        <div className="task-summary">
          <span className="summary-count">{list.count}</span>
          <span className="summary-label">{list.count === 1 ? 'task in view' : 'tasks in view'}</span>
        </div>
        <button type="button" className="btn primary new-task-button" onClick={() => setEditing('new')}>
          <span aria-hidden="true">＋</span> New task
        </button>
      </header>

      {lookups.error && <p className="notice error" role="alert">{lookups.error}</p>}

      <div className="filter-panel">
        <div className="section-kicker"><span>YOUR LIST</span><span>Find your focus</span></div>
        <TaskFilters filters={list.filters} onChange={list.setFilters} onReset={list.resetFilters}
                     canReset={list.hasActiveFilters} categories={lookups.categories}
                     tags={lookups.tags} meta={lookups.meta} />
      </div>

      <BulkBar selectedIds={selected} meta={lookups.meta} onClear={() => setSelected([])}
               onDone={() => { setSelected([]); refresh(); }} />

      {list.error && (
        <p className="notice error" role="alert">
          {list.error} <button type="button" className="link-btn" onClick={list.reload}>Retry</button>
        </p>
      )}

      {list.tasks.length > 0 && (
        <label className="check select-all">
          <input type="checkbox" checked={allSelected}
                 onChange={() => setSelected(allSelected ? [] : list.tasks.map((t) => t.id))} />
          Select all on this page
        </label>
      )}

      <ul className={`task-list ${list.loading ? 'loading' : ''}`} aria-busy={list.loading}>
        {list.tasks.map((task) => (
          <TaskItem key={task.id} task={task} selected={selected.includes(task.id)}
                    onSelect={toggleSelect} onEdit={setEditing} onChanged={refresh} />
        ))}
      </ul>

      {!list.loading && !list.error && list.tasks.length === 0 && (
        <div className="empty task-empty">
          <span className="empty-mark" aria-hidden="true">✓</span>
          {list.hasActiveFilters ? (
            <>
              <h2>No tasks match this view.</h2>
              <p>Try changing a filter or search term.</p>
              <button type="button" className="btn" onClick={list.resetFilters}>Clear filters</button>
            </>
          ) : (
            <>
              <h2>A little room to breathe.</h2>
              <p>Add a task whenever you’re ready.</p>
              <button type="button" className="btn primary" onClick={() => setEditing('new')}>
                Create your first task <span aria-hidden="true">↗</span>
              </button>
            </>
          )}
        </div>
      )}

      <Pagination page={list.page} pageCount={list.pageCount} onChange={list.setPage} />

      {editing && (
        <Modal title={editing === 'new' ? 'New task' : 'Edit task'} onClose={closeForm}>
          <TaskForm task={editing === 'new' ? null : editing} lookups={lookups}
                    onSubmit={save} onCancel={closeForm} />
        </Modal>
      )}
    </main>
  );
};

export default AppPage;
