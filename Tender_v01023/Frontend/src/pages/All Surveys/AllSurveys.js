import React, {useEffect, useState} from 'react';
import './AllSurveys.css';
import {API_URL, FRONTEND_URL} from "../../util/util";
import {useNavigate} from "react-router-dom";

function AllSurveys() {
  const navigate = useNavigate();
  const [surveyData, setSurveyData] = useState([]);

  useEffect(() => {
    fetch(API_URL + "/surveys", {
      headers: {
        'Cache-Control': 'no-cache'
      }
    })
      .then(response => {
        if (response.ok) {
          return response.json();
        }
        throw new Error('Network response was not ok.');
      })
      .then(res => {
        setSurveyData(res);
      })
      .catch(error => console.error('Failed to load data:', error));
  }, []);

  return (
    <div className="survey-container">
      {surveyData.map((survey, index) => (
        <div key={index} className="card">
          <div className="card-content">
            <h3>Survey ID: Survey {survey.id}</h3>
            {/*<h3>Number of Questions ID: Survey {survey.id}</h3>*/}
          </div>
          <div className="card-icon">
            <button className="export-btn" onClick={navigate.bind(this, "/surveys/" + survey.id)}>
              <i className="fas fa-external-link-alt"/>
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}

export default AllSurveys;
