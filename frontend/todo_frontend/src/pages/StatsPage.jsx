import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { tasksApi } from '../api/resources';
import { errorMessage } from '../api/errors';
import { formatDate, formatMinutes } from '../utils/dates';

const RANGES = [7, 14, 30, 90];

const Stat = ({ label, value, tone }) => (
  <div className={`stat ${tone || ''}`}>
    <span className="stat-value">{value}</span>
    <span className="stat-label">{label}</span>
  </div>
);

const TrendChart = ({ series }) => {
  const max = Math.max(1, ...series.flatMap((p) => [p.created, p.completed]));
  const width = 100 / series.length;
  return (
    <figure className="trend">
      <svg viewBox="0 0 100 40" preserveAspectRatio="none" role="img"
           aria-label="Tasks created and completed per day">
        {series.map((p, i) => (
          <g key={p.date}>
            <rect x={i * width + width * 0.08} width={width * 0.4}
                  y={40 - (p.created / max) * 38} height={(p.created / max) * 38} className="bar-created">
              <title>{`${formatDate(p.date)}: ${p.created} created`}</title>
            </rect>
            <rect x={i * width + width * 0.5} width={width * 0.4}
                  y={40 - (p.completed / max) * 38} height={(p.completed / max) * 38} className="bar-completed">
              <title>{`${formatDate(p.date)}: ${p.completed} completed`}</title>
            </rect>
          </g>
        ))}
      </svg>
      <figcaption>
        <span className="legend created">Created</span>
        <span className="legend completed">Completed</span>
        <span className="muted">{formatDate(series[0].date)} – {formatDate(series[series.length - 1].date)}</span>
      </figcaption>
    </figure>
  );
};

const StatsPage = () => {
  const [days, setDays] = useState(30);
  const [stats, setStats] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;
    setError('');
    tasksApi.statistics(days)
      .then((data) => !cancelled && setStats(data))
      .catch((err) => !cancelled && setError(errorMessage(err, 'Could not load statistics.')));
    return () => { cancelled = true; };
  }, [days]);

  if (error) return <main className="page"><p className="notice error" role="alert">{error}</p></main>;
  if (!stats) return <main className="page"><p className="muted" role="status">Loading statistics…</p></main>;

  const { overview, deadlines, breakdown, trend, performance, workload } = stats;

  return (
    <main className="page">
      <div className="page-head">
        <h1>Insights</h1>
        <label className="field compact">
          <span>Period</span>
          <select value={days} onChange={(e) => setDays(Number(e.target.value))}>
            {RANGES.map((r) => <option key={r} value={r}>Last {r} days</option>)}
          </select>
        </label>
      </div>

      {overview.total === 0 && (
        <p className="notice">No data yet. <Link to="/app">Create a task</Link> to get started.</p>
      )}

      <section className="card">
        <h2>Overview</h2>
        <div className="stats">
          <Stat label="Total" value={overview.total} />
          <Stat label="Open" value={overview.open} />
          <Stat label="Completed" value={overview.by_status.Completed} />
          <Stat label="Completion rate" value={`${overview.completion_rate}%`} />
          <Stat label="Overdue" value={deadlines.overdue} tone={deadlines.overdue ? 'danger' : ''} />
          <Stat label="Due today" value={deadlines.due_today} />
          <Stat label="Due in 7 days" value={deadlines.due_next_7_days} />
          <Stat label="No due date" value={deadlines.no_due_date} />
        </div>
      </section>

      <section className="card">
        <h2>Activity</h2>
        <TrendChart series={trend.series} />
        <div className="stats">
          <Stat label={`Completed (${days}d)`} value={performance.completed_in_window} />
          <Stat label="On-time rate"
                value={performance.on_time_rate == null ? '–' : `${performance.on_time_rate}%`} />
          <Stat label="Avg. time to finish"
                value={performance.avg_completion_hours == null ? '–' : `${performance.avg_completion_hours}h`} />
        </div>
      </section>

      <section className="card">
        <h2>Workload — next 7 days</h2>
        <table className="table">
          <thead>
            <tr><th>Date</th><th>Tasks due</th><th>Estimated time</th><th>Without estimate</th></tr>
          </thead>
          <tbody>
            {workload.next_7_days.map((d) => (
              <tr key={d.date}>
                <td>{formatDate(d.date)}</td>
                <td>{d.tasks}</td>
                <td>{d.estimated_minutes ? formatMinutes(d.estimated_minutes) : '–'}</td>
                <td>{d.tasks_without_estimate || '–'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="card">
        <h2>Open tasks by category</h2>
        {breakdown.open_by_category.length === 0 ? (
          <p className="muted">Nothing open. 🎉</p>
        ) : (
          <ul className="bars">
            {breakdown.open_by_category.map((row) => (
              <li key={row.category}>
                <span>{row.category}</span>
                <progress max={overview.open || 1} value={row.count} aria-label={`${row.category}: ${row.count}`} />
                <b>{row.count}</b>
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
};

export default StatsPage;
