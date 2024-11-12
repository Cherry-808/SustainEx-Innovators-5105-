import React, { useState } from 'react';
import './App.css';

function Feedback() {
  const [feedback, setFeedback] = useState('');

  const handleFeedbackChange = (event) => {
    setFeedback(event.target.value);
  };

  const submitFeedback = () => {
    // Logic to submit feedback
    alert('Feedback submitted: ' + feedback);
  };

  return (
    <div className="feedback-container">
      <h2>Feedback</h2>
      <textarea value={feedback} onChange={handleFeedbackChange} />
      <button onClick={submitFeedback}>Submit Feedback</button>
    </div>
  );
}

export default Feedback;
