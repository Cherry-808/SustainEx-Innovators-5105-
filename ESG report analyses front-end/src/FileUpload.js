import React, { useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import { FaUpload } from "react-icons/fa";

function FileUpload() {
  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState(null);

  const onFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile && selectedFile.type !== "application/pdf") {
      alert("Please upload a valid PDF file.");
      return;
    }
    setFile(selectedFile);
  };

  const onFileUpload = async () => {
    if (!file) {
      setUploadStatus("Please select a file before uploading.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post("http://127.0.0.1:5000/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      if (response.status === 200) {
        setUploadStatus("File uploaded successfully! Analysis is in progress...");
        console.log("Response from server:", response.data);
      } else {
        setUploadStatus("Failed to upload file. Please try again.");
      }
    } catch (error) {
      console.error("Error uploading file:", error);
      setUploadStatus("Error occurred while uploading. Please check console for details.");
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
            />

            <button className="upload-btn" onClick={onFileUpload}>
              <FaUpload style={{ marginRight: "0.5rem" }} /> Upload!
            </button>

            <button className="upload-btn">
              <FaUpload style={{ marginRight: "0.5rem" }} /> Start
            </button>
          </div>
        </div>

        {uploadStatus && <p className="upload-status">{uploadStatus}</p>}

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
