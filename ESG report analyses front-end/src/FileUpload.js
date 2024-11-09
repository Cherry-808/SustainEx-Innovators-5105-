import React, { useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import { FaUpload } from "react-icons/fa"; // 上传图标

function FileUpload() {
  const [file, setFile] = useState(null);

  const onFileChange = event => {
    setFile(event.target.files[0]);
  };

  const onFileUpload = () => {
    const formData = new FormData();
    formData.append("file", file);
    // Replace 'your-upload-url' with the endpoint to which the file is to be posted.
    axios.post("your-upload-url", formData);
  };

  return (
    <div className="file-upload">
      <h2>Upload Your Report</h2>
      <div className="upload-section">
      <p className="upload-instructions">Please upload a PDF file. Maximum size: 10MB.</p>
      <label htmlFor="file" className="upload-btn">
        <FaUpload style={{ marginRight: "0.5rem" }} /> Select File</label>
      <input type="file" id="file" className="file-input" />
      <button className="upload-btn">
      <FaUpload style={{ marginRight: "0.5rem" }} /> Upload!</button>
      </div>
      <div className="results-link">
      <Link to="/results">Go to Analysis Results</Link>
      </div>
    </div>
  );
}

export default FileUpload;