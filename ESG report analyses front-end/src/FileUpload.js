import React, { useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import { FaUpload } from "react-icons/fa"; // 上传图标


function FileUpload() {
  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState(null); // 用于显示上传状态


  // 处理文件选择
  const onFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile && selectedFile.type !== "application/pdf") {
        alert("Please upload a valid PDF file.");
        return;
    }
    setFile(selectedFile);
};


  // 上传文件到后端
  const onFileUpload = async () => {
    if (!file) {
      setUploadStatus("Please select a file before uploading.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      // 调用后端 API（请将 'http://127.0.0.1:5000/upload' 替换为你的实际后端地址）
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
    <div className="file-upload">
      <h2>Upload Your Report</h2>
      <div className="upload-section">
        <p className="upload-instructions">Please upload a PDF file. Maximum size: 10MB.</p>
        
        {/* 文件选择 */}
        <label htmlFor="file" className="upload-btn">
          <FaUpload style={{ marginRight: "0.5rem" }} /> Select File
        </label>
        <input
          type="file"
          id="file"
          className="file-input"
          onChange={onFileChange} // 文件选择事件
        />

        {/* 上传按钮 */}
        <button className="upload-btn" onClick={onFileUpload}>
          <FaUpload style={{ marginRight: "0.5rem" }} /> Upload!
        </button>
      </div>

      {/* 上传状态信息 */}
      {uploadStatus && <p className="upload-status">{uploadStatus}</p>}

      {/* 分析结果链接 */}
      <div className="results-link">
        <Link to="/results">Go to Analysis Results</Link>
      </div>
    </div>
  );
}

export default FileUpload;