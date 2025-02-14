import React from 'react';
import { motion } from 'framer-motion';

const Square = ({ index, hasTick }) => {
  return (
    <motion.div
      className={`square ${hasTick ? 'has-tick' : ''}`}
      initial={{ scale: 0 }}
      animate={{ scale: 1 }}
      transition={{ duration: 0.5, delay: index * 0.05 }}
    >
      {hasTick && <span className="tick">✓</span>}
    </motion.div>
  );
};

export default Square;