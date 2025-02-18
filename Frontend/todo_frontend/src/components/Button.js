import React from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';

const Button = () => {
  const navigate = useNavigate();

  return (
    <div className="cta-container">
      <motion.button
        className="cta-button"
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1, delay: 1 }}
        onClick={() => navigate('/app')}
      >
        Create now!
      </motion.button>
    </div>
  );
};

export default Button;
