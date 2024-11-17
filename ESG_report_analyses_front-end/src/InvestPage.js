
import React from 'react';

function InvestPage() {
  return (
    <div style={{ height: "100vh", width: "100vw", overflow: "hidden" }}>
      <iframe
        src="http://localhost:8501"
        title="Streamlit App"
        style={{
          width: "100%", // 宽度100%
          height: "100%", // 高度100%
          border: "none", // 去掉边框
        }}
      ></iframe>
    </div>
  );
}

export default InvestPage;