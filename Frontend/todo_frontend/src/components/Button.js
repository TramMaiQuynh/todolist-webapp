import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';

const Button = () => {
  return (
    <div className="cta-container">
      <motion.button
        className="cta-button"
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1, delay: 1 }}
      >
        <Link to="/app">Create now!</Link>
      </motion.button>
    </div>
  );
};

export default Button;