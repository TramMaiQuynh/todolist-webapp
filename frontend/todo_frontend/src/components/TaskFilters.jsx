import React from 'react';

const ORDERINGS = [
  { value: '-created_at', label: 'Newest first' },
  { value: 'created_at', label: 'Oldest first' },
  { value: 'due_date', label: 'Due date (soonest)' },
  { value: '-due_date', label: 'Due date (latest)' },
  { value: '-priority_rank', label: 'Priority (high → low)' },
  { value: 'priority_rank', label: 'Priority (low → high)' },
  { value: 'title', label: 'Title A–Z' },
];

const Select = ({ label, value, onChange, children }) => (
  <label className="field compact">
    <span>{label}</span>
    <select value={value} onChange={(e) => onChange(e.target.value)}>
      {children}
    </select>
  </label>
);

const TaskFilters = ({ filters, onChange, onReset, canReset, categories, tags, meta }) => (
  <section className="filters" aria-label="Filters">
    <label className="field compact grow">
      <span>Search</span>
      <input
        type="search"
        value={filters.search}
        placeholder="Search title or description"
        onChange={(e) => onChange({ search: e.target.value })}
      />
    </label>

    <Select label="Status" value={filters.status} onChange={(status) => onChange({ status })}>
      <option value="">All</option>
      {meta.statuses.map((s) => <option key={s.key} value={s.key}>{s.label}</option>)}
    </Select>

    <Select label="Priority" value={filters.priority} onChange={(priority) => onChange({ priority })}>
      <option value="">All</option>
      {meta.priorities.map((p) => <option key={p.key} value={p.key}>{p.label}</option>)}
    </Select>

    <Select label="Category" value={filters.category} onChange={(category) => onChange({ category })}>
      <option value="">All</option>
      {categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
    </Select>

    <Select label="Tag" value={filters.tag} onChange={(tag) => onChange({ tag })}>
      <option value="">All</option>
      {tags.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
    </Select>

    <Select label="Due" value={filters.due} onChange={(due) => onChange({ due })}>
      <option value="">Any time</option>
      <option value="overdue">Overdue</option>
      <option value="today">Due today</option>
    </Select>

    <Select label="View" value={filters.archived} onChange={(archived) => onChange({ archived })}>
      <option value="false">Active</option>
      <option value="true">Archived</option>
      <option value="all">All</option>
    </Select>

    <Select label="Sort by" value={filters.ordering} onChange={(ordering) => onChange({ ordering })}>
      {ORDERINGS.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
    </Select>

    <label className="check">
      <input
        type="checkbox"
        checked={filters.important}
        onChange={(e) => onChange({ important: e.target.checked })}
      />
      Important only
    </label>

    {canReset && (
      <button type="button" className="btn ghost" onClick={onReset}>Clear filters</button>
    )}
  </section>
);

export default TaskFilters;
