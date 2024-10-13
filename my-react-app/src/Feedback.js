import React, { useState } from 'react';

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
    <div>
      <h2>Feedback</h2>
      <textarea value={feedback} onChange={handleFeedbackChange} />
      <button onClick={submitFeedback}>Submit Feedback</button>
    </div>
  );
}

export default Feedback;