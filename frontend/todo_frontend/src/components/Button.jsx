import React from 'react';
import { useNavigate } from 'react-router-dom';

const Button = () => {
  const navigate = useNavigate();

  return (
    <div className="cta-container">
      <button
        className="btn primary cta-button"
        onClick={() => navigate('/register')}
      >
        Get started <span aria-hidden="true">↗</span>
      </button>
    </div>
  );
};

export default Button;
