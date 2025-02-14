// import logo from './logo.svg';
// import './App.css';

// function App() {
//   return (
//     <div className="Homepage">
//       <header className="App-header">
//         <img src={logo} className="App-logo" alt="logo" />
//         <p>
//           Edit <code>src/App.js</code> and save to reload.
//         </p>
//         <a
//           className="App-link"
//           href="https://reactjs.org"
//           target="_blank"
//           rel="noopener noreferrer"
//         >
//           Learn React
//         </a>
//       </header>
//     </div>
//   );
// }

// export default App;

import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import HomePage from './pages/HomePage';
import AppPage from './pages/AppPage';
import Footer from './components/Footer'
import { ToastContainer } from 'react-toastify';


const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/app" element={<AppPage />} />
      </Routes>
      <Footer />  {/* Footer luôn xuất hiện dưới cùng của trang */}
      <ToastContainer/> {/* Toast thong bao khi can*/}
    </Router>
  );
};

export default App;


