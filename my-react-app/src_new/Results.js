import React, { useState } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import './Results.css';

function Results() {
  const [score, setScore] = useState(85); // 示例分数
  const [analysisData, setAnalysisData] = useState([
    { metric: "Accuracy", value: 90 },
    { metric: "Completeness", value: 85 },
    { metric: "Timeliness", value: 80 },
  ]);
  const [chartData, setChartData] = useState([
    { name: "Week 1", value: 4000 },
    { name: "Week 2", value: 3000 },
    { name: "Week 3", value: 2000 },
    { name: "Week 4", value: 2780 },
    { name: "Week 5", value: 1890 },
  ]);

  // 圆形进度条计算
  const radius = 50; // 圆的半径
  const circumference = 2 * Math.PI * radius; // 圆的周长
  const progress = (score / 100) * circumference; // 当前分数对应的周长部分

  return (
    <div className="results">
      <header className="header">
        <h1>Report Analysis Results</h1>
        <a href="/">Go Back to Home</a>
      </header>

      <div className="card-container">
        {/* 圆形进度条 */}
        <div className="card">
          <section className="score-section">
            <h2>Report Score</h2>
            <div className="circle-progress">
              <svg width="120" height="120">
                {/* 背景圆 */}
                <circle
                  cx="60"
                  cy="60"
                  r={radius}
                  stroke="#f1f1f1"
                  strokeWidth="10"
                  fill="none"
                />
                {/* 动态进度圆 */}
                <circle
                  cx="60"
                  cy="60"
                  r={radius}
                  stroke="#4caf50"
                  strokeWidth="10"
                  fill="none"
                  strokeDasharray={circumference}
                  strokeDashoffset={circumference - progress} // 动态调整进度
                  strokeLinecap="round"
                  style={{ transition: "stroke-dashoffset 0.5s ease" }} // 动画
                />
              </svg>
              <div className="score-text">{score}%</div>
            </div>
          </section>
        </div>

        {/* Analysis Data Section */}
        <div className="card">
          <section className="table-section">
            <h3>Analysis Data</h3>
            <table>
              <thead>
                <tr>
                  <th>Metric</th>
                  <th>Value</th>
                </tr>
              </thead>
              <tbody>
                {analysisData.map((row, index) => (
                  <tr key={index}>
                    <td>{row.metric}</td>
                    <td>{row.value}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        </div>

        {/* Performance Over Time Section */}
        <div className="card">
          <section className="visualization-section">
            <h3>Performance Over Time</h3>
            <ResponsiveContainer width="90%" height={250}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="value" stroke="#4caf50" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </section>
        </div>
      </div>
    </div>
  );
}

export default Results;