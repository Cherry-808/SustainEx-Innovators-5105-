import React, { useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import { FaUpload } from "react-icons/fa";
import ProcessControl from './ProcessControl';  // 新增这行

function FileUpload() {
  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

  const onFileChange = (event) => {
    const selectedFile = event.target.files[0];
    setErrorMessage('');
    
    if (!selectedFile) {
      return;
    }

    if (selectedFile.type !== "application/pdf") {
      setErrorMessage("Please upload a valid PDF file.");
      return;
    }

    if (selectedFile.size > 10 * 1024 * 1024) {  // 10MB limit
      setErrorMessage("File size exceeds 10MB limit.");
      return;
    }

    setFile(selectedFile);
    setUploadStatus(null);
  };

  const onFileUpload = async () => {
    if (!file) {
      setUploadStatus("Please select a file before uploading.");
      return;
    }

    setIsLoading(true);
    setErrorMessage('');
    const formData = new FormData();
    formData.append("file", file);


    try {
      const response = await axios.post(`${API_URL}/upload_pdf`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          setUploadStatus(`Upload progress: ${percentCompleted}%`);
        },
      });

      if (response.status === 200) {
        setUploadStatus("File uploaded successfully! Analysis is in progress...");
        console.log("Response from server:", response.data);
      } 
    } catch (error) {
      console.error("Error uploading file:", error);
      if (error.response) {
        // Server responded with error
        setErrorMessage(error.response.data.error || "Server error occurred");
      } else if (error.request) {
        // Request made but no response
        setErrorMessage("Could not connect to server. Please check if the server is running.");
      } else {
        // Error in request setup
        setErrorMessage("Error preparing upload. Please try again.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="file-upload-container">
      <div className="file-upload-content">
        <div className="project-introduction">
          <h1 className="project-title">Automated ESG Data Extraction and Performance Analysis Project</h1>
          <p className="project-description">
            Environmental, Social, and Governance (ESG) reporting has become increasingly crucial for businesses and investors. 
            However, the process of extracting relevant ESG information from unstructured reports is often time-consuming and 
            labor-intensive. Additionally, evaluating ESG performance across companies and industries remains challenging due 
            to the lack of standardized, easily comparable data.
          </p>
          <p className="project-description">
            This project aims to develop an innovative system that automates the extraction of ESG information from 
            unstructured reports and provides a comprehensive analysis of ESG performance within selected industries. 
            By leveraging advanced natural language processing (NLP) techniques and data analysis, the project seeks to 
            streamline the ESG data extraction process, improve data quality, and offer valuable insights into corporate 
            sustainability practices.
          </p>
        </div>

        <div className="upload-section">
          <h2 className="upload-title">Upload Your Report</h2>
          <p className="upload-instructions">Please upload a PDF file. Maximum size: 10MB.</p>
          
        <div className="button-group">
          <label htmlFor="file" className="upload-btn">
              <FaUpload style={{ marginRight: "0.5rem" }} /> Select File
            </label>
            <input
              type="file"
              id="file"
              className="file-input"
              onChange={onFileChange}
              accept=".pdf"
              disabled={isLoading}
            />
          

            <button 
             className="upload-btn" 
             onClick={onFileUpload}
             disabled={!file || isLoading}
        >
             <FaUpload style={{ marginRight: "0.5rem" }} />
             {isLoading ? 'Uploading...' : 'Upload!'}
        </button>
        </div>
   
        
            {/* 新增这个组件 */}
        <ProcessControl />
        
        {errorMessage && <p className="error-message">{errorMessage}</p>}
        {uploadStatus && <p className="upload-status">{uploadStatus}</p>}
        </div>
      
        <div className="results-link">
          <Link to="/results" className="analysis-button">Go to Analysis Results</Link>
        </div>
   
    </div>
      <style jsx>{`
        .file-upload-container {
          display: flex;
          justify-content: center;
          align-items: center;
          min-height: calc(100vh - 60px);
          padding: 20px;
        }

        .file-upload-content {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 30px;
          max-width: 800px;
          width: 100%;
          text-align: center;
        }

        .project-introduction {
          text-align: left;
          width: 100%;
          margin-bottom: 20px;
        }

        .project-title {
          font-size: 1.8rem;
          color: #2e7d32;
          margin-bottom: 20px;
          text-align: center;
        }

        .project-description {
          font-size: 1rem;
          line-height: 1.6;
          color: #555;
          margin-bottom: 15px;
          text-align: justify;
        }

        .upload-section {
          width: 100%;
          padding: 30px;
          border-radius: 8px;
          background-color: #f8f8f8;
          margin-top: 20px;
        }

        .upload-title {
          font-size: 1.5rem;
          color: #333;
          margin-bottom: 15px;
        }

        .upload-instructions {
          color: #666;
          margin: 10px 0 20px;
        }

        .button-group {
          display: flex;
          gap: 15px;
          justify-content: center;
          margin: 20px 0;
        }

        .upload-btn {
          background-color: #4CAF50;
          color: white;
          padding: 10px 20px;
          border: none;
          border-radius: 5px;
          cursor: pointer;
          display: flex;
          align-items: center;
          font-size: 1rem;
          transition: background-color 0.3s;
        }

        .upload-btn:hover {
          background-color: #45a049;
        }

        .file-input {
          display: none;
        }

        .upload-status {
          color: #666;
          margin: 10px 0;
        }

        .analysis-button {
          display: inline-block;
          padding: 10px 20px;
          border: 2px solid #4CAF50;
          border-radius: 5px;
          color: #4CAF50;
          text-decoration: none;
          transition: all 0.3s;
          margin-top: 10px;
        }

        .analysis-button:hover {
          background-color: #4CAF50;
          color: white;
        }
      `}</style>
    </div>
  );
}

export default FileUpload;