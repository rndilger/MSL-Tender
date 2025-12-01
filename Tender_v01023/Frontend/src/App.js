import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import CreateSurvey from './pages/Create Survey/CreateSurvey';
import Survey from './pages/Survey/Survey';
import AllSurveys from './pages/All Surveys/AllSurveys';
import Navbar from './common/Navbar/Navbar';
import Login from "./pages/Login/Login";
import Footer from "./common/Footer/Footer";

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(localStorage.getItem('isLoggedIn') === 'true');

  const handleLoginSuccess = () => {
    setIsLoggedIn(true);
  };


  return (
    <Router>
      {isLoggedIn && <Navbar />}
      <div className="App">
        <Routes>
          <Route path="/login" element={!isLoggedIn ? <Login onLoginSuccess={handleLoginSuccess} /> : <Navigate to="/create-survey" />} />
          <Route path="/surveys/:id" element={isLoggedIn ? <Survey /> : <Navigate to="/login" />} />
          <Route path="/all-surveys" element={isLoggedIn ? <AllSurveys /> : <Navigate to="/login" />} />
          <Route path="/" element={isLoggedIn ? <CreateSurvey /> : <Navigate to="/login" />} />
        </Routes>
      </div>
      {isLoggedIn && <Footer />}
    </Router>
  );
}

export default App;
