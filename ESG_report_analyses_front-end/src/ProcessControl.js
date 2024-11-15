import React, { useState } from 'react';
import axios from 'axios';
import { FaPlay, FaChartLine } from "react-icons/fa";
import { useNavigate } from 'react-router-dom';

function ProcessControl() {
  const [processStatus, setProcessStatus] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const navigate = useNavigate();
  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

  const startProcess = async () => {
    try {
      setIsProcessing(true);
      setProcessStatus('Processing PDF...');
      const response = await axios.post(`${API_URL}/start_process`);
      setProcessStatus(response.data.message);

      if (response.data.status === 'success') {
        setTimeout(() => {
          setProcessStatus('PDF processing completed! You can now generate ESG analysis.');
        }, 1000);
      }
    } catch (error) {
      setProcessStatus('Process failed: ' + (error.response?.data?.error || error.message));
    } finally {
      setIsProcessing(false);
    }
  };

  const generateESGAnalysis = async () => {
    try {
      setIsAnalyzing(true);
      setProcessStatus('Generating ESG analysis...');
      
      const response = await axios.post('http://localhost:5000/analyze_esg');
      
      if (response.data.status === 'success') {
        setProcessStatus('ESG analysis completed! Redirecting to results...');
        setTimeout(() => {
          navigate('/results');
        }, 1500);
      }
    } catch (error) {
      setProcessStatus('Analysis failed: ' + (error.response?.data?.error || error.message));
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="process-control">
      <div style={{ display: 'flex', gap: '10px', justifyContent: 'center' }}>
        {/* Process PDF Button */}
        <button 
          className="process-btn" 
          onClick={startProcess}
          disabled={isProcessing}
          style={{
            backgroundColor: '#4CAF50',
            color: 'white',
            padding: '10px 20px',
            border: 'none',
            borderRadius: '4px',
            cursor: isProcessing ? 'not-allowed' : 'pointer',
            opacity: isProcessing ? 0.7 : 1,
            display: 'flex',
            alignItems: 'center',
            fontSize: '1rem',
            transition: 'background-color 0.3s'
          }}
        >
          <FaPlay style={{ marginRight: "0.5rem" }} />
          {isProcessing ? 'Processing...' : 'Start Process'}
        </button>
        </div>

      

      {/* Status Message */}
      {processStatus && (
        <div
          style={{
            marginTop: '10px',
            padding: '10px',
            borderRadius: '4px',
            backgroundColor: processStatus.includes('failed') ? '#ffebee' : '#e8f5e9',
            color: processStatus.includes('failed') ? '#d32f2f' : '#2e7d32',
            textAlign: 'center',
            maxWidth: '100%',
            width: '100%',
            fontSize: '0.9rem',
            transition: 'all 0.3s',
            animation: 'fadeIn 0.3s ease-in'
          }}
        >
          {processStatus}
        </div>
      )}

      <style jsx>{`
        .process-control {
          display: flex;
          flex-direction: column;
          align-items: center;
          width: 100%;
          gap: 10px;
          margin-top: 20px;
        }

        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .process-btn:hover:not(:disabled),
        .analyze-btn:hover:not(:disabled) {
          transform: translateY(-1px);
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .process-btn:active:not(:disabled),
        .analyze-btn:active:not(:disabled) {
          transform: translateY(0);
          box-shadow: none;
        }
      `}</style>
    </div>
  );
}

export default ProcessControl;