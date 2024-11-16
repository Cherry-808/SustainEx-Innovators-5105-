import React from "react";
import { useNavigate } from "react-router-dom";
import './Results.css';
import FinalSummary from './FinalSummary';

function Results() {
  const navigate = useNavigate();



  return (
    <div className="results-container">
    {/* 侧边导航栏 */}
    <nav className="sidebar">
  <ul>
    <li>
      <a href="#total-score">
        <i className="fas fa-chart-pie"></i> Total Score
      </a>
    </li>
    <li>
      <a href="#key-indicators">
        <i className="fas fa-tasks"></i> Key Indicator Scores
      </a>
    </li>
    <li>
      <a href="#choose-report">
        <i className="fas fa-file-alt"></i> Choose a Report
      </a>
    </li>
    <li>
      <a href="#more-about-report">
        <i className="fas fa-info-circle"></i> More
      </a>
    </li>
  </ul>
</nav>
      {/* 主内容 */}
      <div className="main-content">

    <div className="results">
      <header className="header">
        <h1>Report Analysis Results</h1>
        <a href="/">Go Back to Home</a>
      </header>

          {/* 文本框 */}
          <div id="total-score" className="text-container">
          <header className="text-box">
      <h1 className="small-title">Total-score</h1>
    </header>
  </div>

          {/* 上方卡片容器 */}
          <div className="card-container">
      <iframe
        src="http://127.0.0.1:5100/api/dashboard" // Flask 提供的 API 地址
        width="100%"
        height="400"
        style={{ border: "none" }}
        title="ESG Dashboard"
    ></iframe>
        </div>

        {/* 指标得分文本框 */}
        <div id="key-indicators" className="text-container">
  <header className="text-box">
    <h1 className="small-title">Key Indicator Scores in ESG Reports (on a 10-Point Scale)</h1>
    <p>This section provides an overview of important ESG metrics based on recent analysis.</p>
    
  </header>
</div>

      {/* 动态卡片 */}
      <div className="dynamic-card-container">
        <iframe
        src="http://127.0.0.1:5100/api/histogram" 
        width="100%"
        height="400"
        style={{ border: "none" }}
        title="ESG Dashboard"
    ></iframe>
      </div>

          {/* 报告选择文本框 */}
          <div id="choose-report" className="text-container">
  <header className="text-box">
    <h1 className="small-title">Choose a customised ESG integrated analysis report</h1>
    <p>1. Investor Report<p></p>
    Obtain key ESG indicators and comprehensive analyses that are closely related to investors' interests. The report focuses on return on investment risks, corporate sustainability potential and social responsibility performance, providing data to support your investment decisions.<p>
</p>2. Authority Report
<p></p>A detailed presentation of ESG compliance and key metrics to help regulators assess a company's environmental, social and governance performance. The report provides comprehensive compliance review data and potential recommendations for improvement to ensure that the company's operations meet regulatory requirements.</p>
<p></p>3. Corporate Executives Report
<p></p>Designed for corporate executives, this report provides a comprehensive view of corporate ESG performance and opportunities for strategic optimisation. The report covers key environmental, social, and governance data to provide strategic support and insights for corporate sustainability decisions.
  </header>
</div>

      {/* 三个卡片 */}
      <div className="card-container three-cards">
  <a href="http://127.0.0.1:5100/report/authority" target="_blank" rel="noopener noreferrer" className="card">
    <h3>Authority Report</h3>
    <p>View ESG report for authorities.</p>
  </a>
  <a href="http://127.0.0.1:5100/report/corporate_executives" target="_blank" rel="noopener noreferrer" className="card">
    <h3>Corporate Executives Report</h3>
    <p>View ESG report for corporate executives.</p>
  </a>
  <a href="http://127.0.0.1:5100/report/investor" target="_blank" rel="noopener noreferrer" className="card">
    <h3>Investor Report</h3>
    <p>View ESG report for investors.</p>
  </a>
</div>
   

 {/* 更多报告信息文本框 */}
 <div id="more-about-report" className="text-container">
          <header className="text-box">
      <h1 className="small-title">Want to know more about the report?</h1>
      <p></p>We will apply AI models and text analytics to extract information from your uploaded corporate ESG reports related to <b>Human Capital Development, Innovation Management, Occupational Health & Safety, Climate Strategy, Human Rights, Environmental Policy & Management Systems, Employees Gender & Age Diversity, Operational Eco-Efficiency, Low Carbon Strategy, Water Related, and other ESG issues. Rights, Environmental Policy & Management Systems, Employee Gender & Age Diversity, Operational Eco-Efficiency, Low Carbon Strategy, Water Related Risks, Business Ethics, Corporate Governance, Green House Gas Emissions, Supply Chain Management, Waste Generation, Labour Practice Indicators. Average Training Hours Per Employee</b> and other key content related to 17 dimensions.
      <p></p>Note: If you are interested in the above, please press the button below to start the analysis. Please be patient as the model takes a long time to run. Thank you for your understanding.
    </header>
  </div>

  {/* 新增这个组件 */}
  <div>
  <FinalSummary />
  </div>

  <div>
      <h1>Personalized ESG Investment Strategies</h1>
      <iframe
        src="http://localhost:8501"
        title="Streamlit App"
        width="800"
        height="600"
        style={{ border: "none" }}
      ></iframe>
    </div>

        </div>
      </div>
    </div>
  );
}

export default Results;