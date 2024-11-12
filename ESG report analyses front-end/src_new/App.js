import FileUpload from './FileUpload';
import Results from './Results';
import Feedback from './Feedback';
import HistoryPage from './HistoryPage';
import React from 'react';
import './App.css'; 
import { BrowserRouter as Router, Routes, Route, NavLink } from "react-router-dom";
import { FaHome, FaHistory, FaCommentDots } from "react-icons/fa";
import { FaLeaf } from "react-icons/fa";

function App() {
  return (
    <Router>
      <div className="App">
        <header className="App-header">
        <h1><FaLeaf style={{ marginRight: "0.5rem", color: "#4caf50" }} />ESG Report Analyzer</h1>
          <nav className="navbar">
            <NavLink to="/" className={({ isActive }) => (isActive ? "active" : "")}>
              <FaHome style={{ marginRight: "0.5rem" }} />
              Home
            </NavLink>
            <NavLink to="/history" className={({ isActive }) => (isActive ? "active" : "")}>
              <FaHistory style={{ marginRight: "0.5rem" }} />
              History
            </NavLink>
            <NavLink to="/feedback" className={({ isActive }) => (isActive ? "active" : "")}>
              <FaCommentDots style={{ marginRight: "0.5rem" }} />
              Feedback
            </NavLink>
          </nav>
        </header>
        <main className="main-content">
          <Routes>
            <Route path="/" element={<FileUpload />} />
            <Route path="/feedback" element={<Feedback />} />
            <Route path="/history" element={<HistoryPage />} />
            <Route path="/results" element={<Results />} />
          </Routes>
        </main>
        <footer className="App-footer">
          <p>Contact Us | Privacy Policy</p>
        </footer>
      </div>
    </Router>
  );
}
export default App;