import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import FileUpload from './FileUpload';
import AnalysisResults from './AnalysisResults';
import Feedback from './Feedback';
import HistoryPage from './HistoryPage';

function App() {
  return (
    <Router>
      <div className="App">
        <header className="App-header">
          <h1>ESG Report Analyzer</h1>
          <nav>
            <Link to="/">Home</Link> | 
            <Link to="/history">History</Link> | 
            <Link to="/feedback">Feedback</Link>
          </nav>
        </header>

        {/* 使用 Routes 包裹所有 Route */}
        <Routes>
          <Route path="/" element={<FileUpload />} />
          <Route path="/results" element={<AnalysisResults />} />
          <Route path="/feedback" element={<Feedback />} />
          <Route path="/history" element={<HistoryPage />} />
        </Routes>

        <footer>
          <p>Contact Us | Privacy Policy</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;