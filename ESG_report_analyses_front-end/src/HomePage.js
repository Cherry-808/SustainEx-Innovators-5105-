import React from "react";
import { Carousel } from "react-responsive-carousel";
import "react-responsive-carousel/lib/styles/carousel.min.css"; // 引入默认样式

function HomePage() {
  return (
    <div style={styles.container}>

      {/* 添加轮播组件 */}
      <Carousel
        showThumbs={false}
        autoPlay={true}
        infiniteLoop={true}
        interval={5000}
        showStatus={false}
        dynamicHeight={false}
        style={{ marginBottom: "20px"} }
      >
        <div>
          <img
            src=" https://cdn.prod.website-files.com/604915c3f8006b714c1fa12d/62860c9e66ee75e65f466c7f_esg%20climate%20action(1)-p-1080.jpeg"
            style={styles.image} // 控制图片大小
          />
        </div>
        <div>
        
          <img
            src="https://images.pexels.com/photos/1230157/pexels-photo-1230157.jpeg"
            style={styles.image} // 控制图片大小
          />
          
        </div>
        <div>
          <img
            src="https://images.pexels.com/photos/532192/pexels-photo-532192.jpeg"
            style={styles.image}
          />
        
        </div>
        <div>
          <img
            src="https://images.pexels.com/photos/110844/pexels-photo-110844.jpeg"
            style={styles.image}
          />
          
        </div>
      </Carousel>

      {/* 标题和描述 */}
      <p> </p>
      <h1 style={styles.title}>Automated ESG Data Extraction and Performance Analysis</h1>
      <p style={styles.description}>
        Environmental, Social, and Governance (ESG) reporting has become increasingly crucial for businesses and
        investors. However, the process of extracting relevant ESG information from unstructured reports is often
        time-consuming and labor-intensive. Additionally, evaluating ESG performance across companies and
        industries remains challenging due to the lack of standardized, easily comparable data.
      </p>
      <p style={styles.description}>
        This project aims to develop an innovative system that automates the extraction of ESG information from
        unstructured reports and provides a comprehensive analysis of ESG performance within selected industries.
        By leveraging advanced natural language processing (NLP) techniques and data analysis, the project seeks to
        streamline the ESG data extraction process, improve data quality, and offer valuable insights into corporate
        sustainability practices.
      </p>
    </div>
  );
}

// 样式
const styles = {
  container: {
    maxWidth: "900px",
    margin: "0 auto",
    padding: "20px",
    textAlign: "center",
  },
  title: {
    fontSize: "28px",
    color: "#2e7d32",
    marginBottom: "20px",
  },
  description: {
    fontSize: "16px",
    lineHeight: "1.6",
    marginBottom: "20px",
    color: "#555",
    textAlign: "justify", // 优化文字对齐方式
  },
  carousel: {
    margin: "20px 0",
  },
  image: {
    width: "80%", // 控制图片宽度
    height: "350px",
    maxWidth: "600px", // 限制图片最大宽度
    margin: "0 auto",
  },
  legend: {
    fontSize: "14px",
    backgroundColor: "rgba(0, 0, 0, 0.5)", // 半透明背景
    color: "#fff",
    padding: "8px",
    borderRadius: "5px",
  },
  uploadSection: {
    marginTop: "30px",
  },
  uploadTitle: {
    fontSize: "20px",
    marginBottom: "10px",
    color: "#2e7d32",
  },
  uploadDescription: {
    fontSize: "14px",
    marginBottom: "15px",
    color: "#555",
  },
  button: {
    backgroundColor: "#4CAF50",
    color: "white",
    padding: "10px 15px",
    margin: "5px",
    fontSize: "14px",
    border: "none",
    borderRadius: "5px",
    cursor: "pointer",
    transition: "background-color 0.3s ease",
  },
  buttonHover: {
    backgroundColor: "#45a049",
  },
};

export default HomePage;