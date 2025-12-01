import React from 'react';
import { Link } from 'react-router-dom';
import './Navbar.css';

function Navbar() {
    const handleLogout = () => {
        localStorage.removeItem('isLoggedIn'); // Assuming 'isLoggedIn' is stored in localStorage
        window.location.href = '/login'; // Redirect to login page or home page after logout
    };

    return (
      <nav className="navbar">
          <div className="navbar-container">
              <ul className="nav-menu">
                  <li className="nav-item">
                      <Link to="/" className="nav-links">Home</Link>
                  </li>
                  <li className="nav-item">
                      <Link to="/all-surveys" className="nav-links">Surveys</Link>
                  </li>
              </ul>
              <button className="logout-button" onClick={handleLogout}>
                  <i className="fas fa-sign-out-alt"></i> Logout
              </button>
          </div>
      </nav>
    );
}

export default Navbar;
