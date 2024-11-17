import HomePage from './HomePage';
import FileUpload from './FileUpload';
import Results from './Results';
import Feedback from './Feedback';
import InvestPage from './InvestPage';
import Contact from './Contact';
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
              <FaHome style={{ marginRight: "0.3rem" }} />
              Home
            </NavLink>
            <NavLink to="/FileUpload" className={({ isActive }) => (isActive ? "active" : "")}>
              <FaHome style={{ marginRight: "0.3rem" }} />
              FileUpload
            </NavLink>
            <NavLink to="/InvestPage" className={({ isActive }) => (isActive ? "active" : "")}>
              <FaHome style={{ marginRight: "0.3rem" }} />
              Investors
            </NavLink>
            <NavLink to="/feedback" className={({ isActive }) => (isActive ? "active" : "")}>
              <FaHome style={{ marginRight: "0.3rem" }} />
              Feedback
            </NavLink>
            <NavLink to="/contact" className={({ isActive }) => (isActive ? "active" : "")}>
              <FaHome style={{ marginRight: "0.3rem" }} />
              Contact Us
            </NavLink>
          </nav>
        </header>
        <main className="main-content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/FileUpload" element={<FileUpload />} />
            <Route path="/feedback" element={<Feedback />} />
            <Route path="/InvestPage" element={<InvestPage />} />
            <Route path="/results" element={<Results />} />
            <Route path="/contact" element={<Contact />} />
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