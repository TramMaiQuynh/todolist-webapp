import React, { useState } from 'react';
import { toast } from 'react-toastify';
import { errorMessage, fieldErrors } from '../api/errors';

const EMPTY = {
  title: '',
  description: '',
  status: 'Pending',
  priority: 'Medium',
  due_date: '',
  estimated_minutes: '',
  category: '',
  tags: [],
  is_important: false,
  recurrence_frequency: '',
  recurrence_interval: 1,
  recurrence_until: '',
};

const fromTask = (task) => ({
  ...EMPTY,
  ...task,
  description: task.description || '',
  due_date: task.due_date || '',
  estimated_minutes: task.estimated_minutes ?? '',
  category: task.category ?? '',
  recurrence_until: task.recurrence_until || '',
});

/** Chuyển state form thành payload API: chuỗi rỗng -> null cho các trường tùy chọn. */
const toPayload = (form) => ({
  title: form.title.trim(),
  description: form.description,
  status: form.status,
  priority: form.priority,
  due_date: form.due_date || null,
  estimated_minutes: form.estimated_minutes === '' ? null : Number(form.estimated_minutes),
  category: form.category === '' ? null : Number(form.category),
  tags: form.tags,
  is_important: form.is_important,
  recurrence_frequency: form.recurrence_frequency,
  recurrence_interval: Number(form.recurrence_interval) || 1,
  recurrence_until: form.recurrence_frequency ? form.recurrence_until || null : null,
});

const FieldError = ({ message }) =>
  message ? <span className="field-error" role="alert">{message}</span> : null;

const TaskForm = ({ task, lookups, onSubmit, onCancel }) => {
  const isEdit = Boolean(task);
  const { categories, tags, meta, createCategory, createTag } = lookups;
  const [form, setForm] = useState(() => (task ? fromTask(task) : EMPTY));
  const [errors, setErrors] = useState({});
  const [saving, setSaving] = useState(false);
  const [newCategory, setNewCategory] = useState('');
  const [newTag, setNewTag] = useState('');

  const set = (name, value) => setForm((prev) => ({ ...prev, [name]: value }));
  const onField = (e) => {
    const { name, value, type, checked } = e.target;
    set(name, type === 'checkbox' ? checked : value);
  };

  const toggleTag = (id) =>
    set('tags', form.tags.includes(id) ? form.tags.filter((t) => t !== id) : [...form.tags, id]);

  const addCategory = async () => {
    const name = newCategory.trim();
    if (!name) return;
    try {
      const created = await createCategory(name);
      set('category', created.id);
      setNewCategory('');
    } catch (err) {
      toast.error(errorMessage(err));
    }
  };

  const addTag = async () => {
    const name = newTag.trim();
    if (!name) return;
    try {
      const created = await createTag(name);
      set('tags', [...form.tags, created.id]);
      setNewTag('');
    } catch (err) {
      toast.error(errorMessage(err));
    }
  };

  const submit = async (e) => {
    e.preventDefault();
    if (!form.title.trim()) {
      setErrors({ title: 'Title is required.' });
      return;
    }
    setSaving(true);
    setErrors({});
    try {
      await onSubmit(toPayload(form));
    } catch (err) {
      const fields = fieldErrors(err);
      setErrors(fields);
      if (!Object.keys(fields).length) toast.error(errorMessage(err));
    } finally {
      setSaving(false);
    }
  };

  const recurring = Boolean(form.recurrence_frequency);

  return (
    <form className="task-form" onSubmit={submit} noValidate>
      <label className="field">
        <span>Title *</span>
        <input name="title" value={form.title} onChange={onField} maxLength={200} autoFocus
               placeholder="What needs to be done?" />
        <FieldError message={errors.title} />
      </label>

      <label className="field">
        <span>Description</span>
        <textarea name="description" value={form.description} onChange={onField} rows={3} />
        <FieldError message={errors.description} />
      </label>

      <div className="grid-2">
        {isEdit && (
          <label className="field">
            <span>Status</span>
            <select name="status" value={form.status} onChange={onField}>
              {meta.statuses.map((s) => <option key={s.key} value={s.key}>{s.label}</option>)}
            </select>
            <FieldError message={errors.status} />
          </label>
        )}

        <label className="field">
          <span>Priority</span>
          <select name="priority" value={form.priority} onChange={onField}>
            {meta.priorities.map((p) => <option key={p.key} value={p.key}>{p.label}</option>)}
          </select>
        </label>

        <label className="field">
          <span>Due date</span>
          <input type="date" name="due_date" value={form.due_date} onChange={onField} />
          <FieldError message={errors.due_date} />
        </label>

        <label className="field">
          <span>Estimate (minutes)</span>
          <input type="number" name="estimated_minutes" min="1" max="100000"
                 value={form.estimated_minutes} onChange={onField} />
          <FieldError message={errors.estimated_minutes} />
        </label>
      </div>

      <div className="field">
        <label htmlFor="category-select"><span>Category</span></label>
        <div className="inline">
          <select id="category-select" name="category" value={form.category} onChange={onField}>
            <option value="">No category</option>
            {categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
          <input value={newCategory} onChange={(e) => setNewCategory(e.target.value)}
                 placeholder="New category" aria-label="New category name" maxLength={100} />
          <button type="button" className="btn" onClick={addCategory}>Add</button>
        </div>
        <FieldError message={errors.category} />
      </div>

      <div className="field">
        <span>Tags</span>
        <div className="chips">
          {tags.map((t) => (
            <label key={t.id} className={`chip ${form.tags.includes(t.id) ? 'on' : ''}`}>
              <input type="checkbox" checked={form.tags.includes(t.id)} onChange={() => toggleTag(t.id)} />
              {t.name}
            </label>
          ))}
        </div>
        <div className="inline">
          <input value={newTag} onChange={(e) => setNewTag(e.target.value)} placeholder="New tag"
                 aria-label="New tag name" maxLength={50} />
          <button type="button" className="btn" onClick={addTag}>Add</button>
        </div>
        <FieldError message={errors.tags} />
      </div>

      <fieldset className="field recurrence">
        <legend>Repeat</legend>
        <div className="grid-3">
          <label className="field compact">
            <span>Frequency</span>
            <select name="recurrence_frequency" value={form.recurrence_frequency} onChange={onField}>
              <option value="">Does not repeat</option>
              {meta.recurrences.map((r) => <option key={r.key} value={r.key}>{r.label}</option>)}
            </select>
          </label>
          {recurring && (
            <>
              <label className="field compact">
                <span>Every</span>
                <input type="number" name="recurrence_interval" min="1" max="365"
                       value={form.recurrence_interval} onChange={onField} />
              </label>
              <label className="field compact">
                <span>Until (optional)</span>
                <input type="date" name="recurrence_until" value={form.recurrence_until} onChange={onField} />
              </label>
            </>
          )}
        </div>
        <FieldError message={errors.recurrence_frequency || errors.recurrence_interval || errors.recurrence_until} />
        {recurring && !form.due_date && <small className="hint">A repeating task needs a due date.</small>}
      </fieldset>

      <label className="check">
        <input type="checkbox" name="is_important" checked={form.is_important} onChange={onField} />
        Mark as important
      </label>

      {errors.detail && <FieldError message={errors.detail} />}

      <footer className="modal-footer">
        <button type="button" className="btn ghost" onClick={onCancel}>Cancel</button>
        <button type="submit" className="btn primary" disabled={saving}>
          {saving ? 'Saving…' : isEdit ? 'Save changes' : 'Create task'}
        </button>
      </footer>
    </form>
  );
};

export default TaskForm;
