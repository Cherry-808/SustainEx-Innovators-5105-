import React, { useState } from "react";
import "./Contact.css"; // 引入 CSS 文件

const Contact = () => {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    message: "",
  });

  const [submitted, setSubmitted] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log("User submitted:", formData);
    setSubmitted(true);
  };

  return (
    <div className="container">
      <div className="card">
        <h2 className="title">Contact Us</h2>
        <p className="description">
          Feel free to reach out to us via the form below or through our contact
          details.
        </p>

        <div>

          {/* Email Card */}
          <div className="info-card">
            <p>
              <strong>Email:</strong> sustainex5105@gmail.com
            </p>
          </div>

          {/* Phone Card */}
          <div className="info-card">
            <p>
              <strong>Phone:</strong> +65 4321 9876
            </p>
          </div>

          {/* Address Card */}
          <div className="info-card">
            <p>
              <strong>Address:</strong> National University of Singapore Block
              S16 Level 9, 6 Science Drive 2 Singapore 117546
            </p>
          </div>
        </div>

        {submitted ? (
          <div className="thank-you-message">
            <h3>Thank you for reaching out!</h3>
            <p>We will get back to you shortly.</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="form">
            <div className="form-group">
              <label htmlFor="name" className="label">
                Name:
              </label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                required
                className="input"
              />
            </div>
            <div className="form-group">
              <label htmlFor="email" className="label">
                Email:
              </label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                className="input"
              />
            </div>
            <div className="form-group">
              <label htmlFor="message" className="label">
                Message:
              </label>
              <textarea
                id="message"
                name="message"
                value={formData.message}
                onChange={handleChange}
                required
                className="textarea"
              />
            </div>
            <button type="submit" className="button">
              Submit
            </button>
          </form>
        )}
      </div>
    </div>
  );
};

export default Contact;