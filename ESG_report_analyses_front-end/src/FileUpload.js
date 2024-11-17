import React, { useState } from "react";
import axios from "axios";
import { Link } from "react-router-dom";
import { FaUpload } from "react-icons/fa";
import { ScrollMenu } from "react-horizontal-scrolling-menu";
import "react-horizontal-scrolling-menu/dist/styles.css"; // 引入样式
import "./FileUpload.css"; // 自定义样式
import ProcessControl from "./ProcessControl";

function FileUpload() {
  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const API_URL = process.env.REACT_APP_API_URL || "http://localhost:5000";

  const companies = [
    {
      name: "Sembcorp Industries",
      website: "https://www.sembcorp.com",
      description: "Leading sustainable solutions provider in Singapore.",
    },
    {
      name: "First Solar",
      website: "https://www.firstsolar.com",
      description: "One of the largest solar panel manufacturers globally.",
    },
    {
      name: "Vestas",
      website: "https://www.vestas.com",
      description: "A world leader in wind turbine manufacturing.",
    },
    {
      name: "SunPower Corporation",
      website: "https://us.sunpower.com",
      description: "Global innovator in solar energy solutions.",
    },
    {
      name: "Keppel Corporation",
      website: "https://www.kepcorp.com",
      description: "Singapore sustainable energy and urbanization company.",
    },
  ];

  const onFileChange = (event) => {
    const selectedFile = event.target.files[0];
    setErrorMessage("");

    if (!selectedFile) {
      return;
    }

    if (selectedFile.type !== "application/pdf") {
      setErrorMessage("Please upload a valid PDF file.");
      return;
    }

    if (selectedFile.size > 10 * 1024 * 1024) {
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
    setErrorMessage("");
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
        setErrorMessage(error.response.data.error || "Server error occurred");
      } else if (error.request) {
        setErrorMessage("Could not connect to server. Please check if the server is running.");
      } else {
        setErrorMessage("Error preparing upload. Please try again.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    
      <div className="file-upload-container">
        <div className="file-upload-content">
          {/* 水平滚动部分 */}
          <div className="horizontal-scroll-section">
            <h2 className="carousel-title">Top Renewable Energy Companies</h2>
            <div className="auto-scroll-wrapper">
              {companies.map((company, index) => (
                <div className="scroll-card" key={index}>
                  <h3 className="scroll-company">{company.name}</h3>
                  <p className="scroll-description">{company.description}</p>
                  <a
                    href={company.website}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="scroll-link"
                  >
                    Visit Website
                  </a>
                </div>
              ))}
            </div>
          </div>
  

        {/* 文件上传部分 */}
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
              {isLoading ? "Uploading..." : "Upload!"}
            </button>
          </div>

          <ProcessControl />

          {errorMessage && <p className="error-message">{errorMessage}</p>}
          {uploadStatus && <p className="upload-status">{uploadStatus}</p>}
        </div>

        <div className="results-link">
          <Link to="/results" className="analysis-button">
            Go to Analysis Results
          </Link>
        </div>
      </div>
    </div>
  );
}

export default FileUpload;