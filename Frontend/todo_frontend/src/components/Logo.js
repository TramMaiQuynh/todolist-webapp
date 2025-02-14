import React from 'react';
import { motion } from 'framer-motion';

const Logo = () => {
  return (
    <div className="logo-container">
      <motion.img
        src="/logo.png"
        alt="Logo"
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ duration: 1, delay: 2 }}
      />
    </div>
  );
};

export default Logo;