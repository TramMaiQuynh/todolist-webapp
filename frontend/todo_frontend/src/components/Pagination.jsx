import React from 'react';

const Pagination = ({ page, pageCount, onChange }) => {
  if (pageCount <= 1) return null;
  return (
    <nav className="pagination" aria-label="Pagination">
      <button type="button" className="btn" disabled={page <= 1} onClick={() => onChange(page - 1)}>
        ← Prev
      </button>
      <span>Page {page} of {pageCount}</span>
      <button type="button" className="btn" disabled={page >= pageCount} onClick={() => onChange(page + 1)}>
        Next →
      </button>
    </nav>
  );
};

export default Pagination;
