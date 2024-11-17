import React, { useState } from 'react';
import './App.css';

function Feedback() {
  const [feedback, setFeedback] = useState('');
  const [submitted, setSubmitted] = useState(false); // 用于显示提交成功反馈

  const handleFeedbackChange = (event) => {
    setFeedback(event.target.value);
  };

  const submitFeedback = () => {
    if (!feedback.trim()) {
      alert('Please provide some feedback before submitting!');
      return;
    }
    // 提交逻辑，可以扩展为发送到服务器等
    setSubmitted(true); // 设置为已提交
    setTimeout(() => setSubmitted(false), 3000); // 提交成功消息显示3秒
    setFeedback(''); // 清空反馈内容
  };

  // 样式对象
  const styles = {
    textarea: {
      width: '60%',
      minHeight: '100px',
      padding: '10px',
      fontSize: '16px',
      borderRadius: '5px',
      border: '1px solid #ccc',
      marginBottom: '10px',
    },
    button: {
      backgroundColor: '#4CAF50',
      color: 'white',
      padding: '10px 20px',
      fontSize: '16px',
      border: 'none',
      borderRadius: '5px',
      cursor: 'pointer',
      transition: 'background-color 0.3s ease',
    },
    successMessage: {
      backgroundColor: '#e7f9ee',
      color: '#4CAF50',
      padding: '10px',
      borderRadius: '5px',
      marginBottom: '10px',
      textAlign: 'center',
    },
  };

  return (
    <div className="feedback-container">
      <h2>Feedback</h2>
      {submitted && (
        <div className="feedback-success-message" style={styles.successMessage}>
          Thank you for your feedback!
        </div>
      )}
      <textarea
        value={feedback}
        onChange={handleFeedbackChange}
        placeholder="Write your feedback here..."
        style={styles.textarea}
      />
      <button onClick={submitFeedback} style={styles.button}>
        Submit Feedback
      </button>
    </div>
  );
}

export default Feedback;