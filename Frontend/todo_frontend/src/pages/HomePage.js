import React from 'react';
import { motion } from 'framer-motion';
import SquareBoard from '../components/SquareBoard';
//import Logo from '../components/Logo';
import Button from '../components/Button';

const HomePage = () => {
  return (
    <div className="homepage">
      <motion.h1
        className="title"
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ duration: 1, delay: 0.1 }}
      >
        My to-do list
      </motion.h1>
      <SquareBoard />
      {/* <Logo /> */}
      <Button />
    </div>
  );
};

export default HomePage;