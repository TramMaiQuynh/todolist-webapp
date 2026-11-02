import React from 'react';

const Brand = ({ compact = false }) => (
  <span className={`brand-lockup ${compact ? 'compact' : ''}`}>
    <span className="brand-mark" aria-hidden="true">
      <svg viewBox="0 0 24 24" fill="none">
        <path d="m6 12.5 4 4 8-9" stroke="currentColor" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    </span>
    <span className="brand-name">Daymark</span>
  </span>
);

export default Brand;
