import React, { useState } from 'react';
import { toast } from 'react-toastify';
import { tasksApi } from '../api/resources';
import { errorMessage } from '../api/errors';
import { formatDate, formatMinutes } from '../utils/dates';
import { recurrenceLabel, statusLabel } from '../utils/labels';
import SubtaskList from './SubtaskList';

const TaskItem = ({ task, selected, onSelect, onEdit, onChanged }) => {
  const [busy, setBusy] = useState(false);
  const [expanded, setExpanded] = useState(false);

  const archived = Boolean(task.archived_at);
  const completed = task.status === 'Completed';

  const run = async (action, successMessage) => {
    setBusy(true);
    try {
      await action();
      if (successMessage) toast.success(successMessage);
      onChanged();
    } catch (err) {
      toast.error(errorMessage(err));
    } finally {
      setBusy(false);
    }
  };

  const toggleComplete = () =>
    run(() => tasksApi.changeStatus(task.id, completed ? 'Pending' : 'Completed'));

  const remove = () => {
    if (!window.confirm(`Delete "${task.title}"? This cannot be undone.`)) return;
    run(() => tasksApi.remove(task.id), 'Task deleted');
  };

  const classes = [
    'task-item',
    completed && 'is-completed',
    task.is_overdue && 'is-overdue',
    archived && 'is-archived',
  ].filter(Boolean).join(' ');

  return (
    <li className={classes}>
      <div className="task-main">
        <input type="checkbox" aria-label={`Select ${task.title}`} checked={selected}
               onChange={() => onSelect(task.id)} className="select-box" />
        <input type="checkbox" aria-label={completed ? 'Mark as not done' : 'Mark as done'}
               checked={completed} disabled={busy || archived} onChange={toggleComplete}
               className="done-box" />

        <div className="task-body">
          <h3>
            {task.is_important && <span title="Important" aria-label="Important">★ </span>}
            {task.title}
          </h3>
          {task.description && <p className="desc">{task.description}</p>}

          <div className="badges">
            <span className={`badge status-${task.status}`}>{statusLabel(task.status)}</span>
            <span className={`badge prio-${task.priority}`}>{task.priority}</span>
            {task.due_date && (
              <span className={`badge ${task.is_overdue ? 'danger' : ''}`}>
                {task.is_overdue ? 'Overdue · ' : 'Due '}{formatDate(task.due_date)}
              </span>
            )}
            {task.estimated_minutes != null && <span className="badge">~{formatMinutes(task.estimated_minutes)}</span>}
            {task.category_name && <span className="badge category">{task.category_name}</span>}
            {task.tags_detail.map((t) => <span key={t.id} className="badge tag">#{t.name}</span>)}
            {task.recurrence_frequency && (
              <span className="badge">↻ {recurrenceLabel(task.recurrence_frequency, task.recurrence_interval)}</span>
            )}
            {archived && <span className="badge">Archived</span>}
          </div>

          <button type="button" className="link-btn" aria-expanded={expanded}
                  onClick={() => setExpanded((v) => !v)}>
            {task.subtask_count
              ? `Subtasks ${task.subtasks_done}/${task.subtask_count}`
              : 'Subtasks'} {expanded ? '▲' : '▼'}
          </button>
          {task.subtask_count > 0 && (
            <progress className="progress" max={task.subtask_count} value={task.subtasks_done}
                      aria-label="Subtask progress" />
          )}
          {expanded && (
            <SubtaskList parentId={task.id} readOnly={archived} onChanged={onChanged} />
          )}
        </div>

        <div className="task-actions">
          {!archived && <button type="button" className="btn" onClick={() => onEdit(task)} disabled={busy}>Edit</button>}
          {archived ? (
            <button type="button" className="btn" disabled={busy}
                    onClick={() => run(() => tasksApi.restore(task.id), 'Task restored')}>Restore</button>
          ) : (
            <button type="button" className="btn" disabled={busy}
                    onClick={() => run(() => tasksApi.archive(task.id), 'Task archived')}>Archive</button>
          )}
          <button type="button" className="btn danger" onClick={remove} disabled={busy}>Delete</button>
        </div>
      </div>
    </li>
  );
};

export default TaskItem;
