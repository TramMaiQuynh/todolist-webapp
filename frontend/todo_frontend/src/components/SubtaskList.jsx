import React, { useCallback, useEffect, useState } from 'react';
import { toast } from 'react-toastify';
import { tasksApi } from '../api/resources';
import { errorMessage } from '../api/errors';

const SubtaskList = ({ parentId, readOnly, onChanged }) => {
  const [subtasks, setSubtasks] = useState(null);
  const [title, setTitle] = useState('');
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    try {
      const detail = await tasksApi.get(parentId);
      setSubtasks(detail.subtasks);
    } catch (err) {
      toast.error(errorMessage(err, 'Could not load subtasks.'));
      setSubtasks([]);
    }
  }, [parentId]);

  useEffect(() => {
    load();
  }, [load]);

  const run = async (action) => {
    setBusy(true);
    try {
      await action();
      await load();
      onChanged();
    } catch (err) {
      toast.error(errorMessage(err));
    } finally {
      setBusy(false);
    }
  };

  const add = (e) => {
    e.preventDefault();
    const trimmed = title.trim();
    if (!trimmed) return;
    run(async () => {
      await tasksApi.create({ title: trimmed, parent: parentId });
      setTitle('');
    });
  };

  const toggle = (sub) =>
    run(() => tasksApi.changeStatus(sub.id, sub.status === 'Completed' ? 'Pending' : 'Completed'));

  const remove = (sub) => run(() => tasksApi.remove(sub.id));

  if (subtasks === null) return <p className="muted">Loading subtasks…</p>;

  return (
    <div className="subtasks">
      <ul>
        {subtasks.map((sub) => (
          <li key={sub.id} className={sub.status === 'Completed' ? 'done' : ''}>
            <label className="check">
              <input type="checkbox" checked={sub.status === 'Completed'} disabled={busy || readOnly}
                     onChange={() => toggle(sub)} />
              <span>{sub.title}</span>
            </label>
            {!readOnly && (
              <button type="button" className="icon-btn" aria-label={`Delete subtask ${sub.title}`}
                      disabled={busy} onClick={() => remove(sub)}>×</button>
            )}
          </li>
        ))}
        {subtasks.length === 0 && <li className="muted">No subtasks yet.</li>}
      </ul>
      {!readOnly && (
        <form className="inline" onSubmit={add}>
          <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Add a subtask"
                 aria-label="New subtask title" maxLength={200} />
          <button type="submit" className="btn" disabled={busy || !title.trim()}>Add</button>
        </form>
      )}
    </div>
  );
};

export default SubtaskList;
