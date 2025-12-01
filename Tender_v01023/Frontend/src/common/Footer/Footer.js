import React from 'react';
import './Footer.css';

function Footer() {
  return (
    <footer className="footer">
      <div className="footer-container">
        <p>Tender app</p>
        <div className="footer-links">
          <h3>Quick Links</h3>
          <ul>
            <li><a href="/">Home</a></li>
            <li><a href="/all-surveys">Surveys</a></li>
          </ul>
        </div>
      </div>
    </footer>
  );
}

export default Footer;
