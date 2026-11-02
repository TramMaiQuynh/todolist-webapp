import React, { useState } from 'react';
import { toast } from 'react-toastify';
import { tasksApi } from '../api/resources';
import { errorMessage } from '../api/errors';

// Mô tả hiển thị cho từng hành động. Hành động lạ do server thêm sau vẫn hiện (nhãn = tên).
const ACTION_LABELS = {
  complete: 'Complete',
  reopen: 'Reopen',
  archive: 'Archive',
  restore: 'Restore',
  delete: 'Delete',
};
const PLAIN_ACTIONS = Object.keys(ACTION_LABELS);

const BulkBar = ({ selectedIds, meta, onClear, onDone }) => {
  const [busy, setBusy] = useState(false);
  if (selectedIds.length === 0) return null;

  const run = async (payload, confirmMessage) => {
    if (confirmMessage && !window.confirm(confirmMessage)) return;
    setBusy(true);
    try {
      const result = await tasksApi.bulk({ ids: selectedIds, ...payload });
      toast.success(`${result.affected} of ${result.requested} tasks updated`);
      onDone();
    } catch (err) {
      toast.error(errorMessage(err));
    } finally {
      setBusy(false);
    }
  };

  const available = PLAIN_ACTIONS.filter((a) => meta.bulk_actions.includes(a));

  return (
    <div className="bulk-bar" role="region" aria-label="Bulk actions">
      <strong>{selectedIds.length} selected</strong>
      {available.map((action) => (
        <button key={action} type="button" disabled={busy}
                className={`btn ${action === 'delete' ? 'danger' : ''}`}
                onClick={() => run({ action },
                  action === 'delete' ? `Delete ${selectedIds.length} tasks? This cannot be undone.` : null)}>
          {ACTION_LABELS[action]}
        </button>
      ))}
      {meta.bulk_actions.includes('set_priority') && (
        <select aria-label="Set priority" disabled={busy} value=""
                onChange={(e) => e.target.value && run({ action: 'set_priority', priority: e.target.value })}>
          <option value="">Set priority…</option>
          {meta.priorities.map((p) => <option key={p.key} value={p.key}>{p.label}</option>)}
        </select>
      )}
      <button type="button" className="btn ghost" onClick={onClear}>Clear selection</button>
    </div>
  );
};

export default BulkBar;
