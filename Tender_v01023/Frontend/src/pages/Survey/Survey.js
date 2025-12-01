import React, {useEffect, useState} from 'react';
import './Survey.css';
import {API_URL} from "../../util/util";
import {useParams} from 'react-router-dom';

function Survey() {
  const {id} = useParams();

  const [surveyData, setSurveyData] = useState([]);
  const [selectedIndices, setSelectedIndices] = useState(new Array(Math.ceil(surveyData.length / 4)).fill(-1));
  const [selectedImageIds, setSelectedImageIds] = useState([]);

  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    fetch(`${API_URL}/surveys/${id}`, {
      headers: {
        'Cache-Control': 'no-cache'
      }
    })
      .then(response => response.ok ? response.json() : Promise.reject('Network response was not ok.'))
      .then(res => {
        const chopIdsArray = res.chop_ids.split(',');
        setSurveyData(chopIdsArray);
        setSelectedIndices(new Array(Math.ceil(chopIdsArray.length / 4)).fill(-1));
        setSelectedImageIds(new Array(chopIdsArray.length).fill(false));
      })
      .catch(error => {
        console.error('Failed to load data:', error);
        setError('Failed to load survey data.');
      });
  }, [id]);

  const handleInputChange = (e, setter) => {
    setter(e.target.value);
    setError('');
  };

  const handleSelectImage = (index) => {
    const setIndex = Math.floor(index / 4);
    const newSelectedIndices = [...selectedIndices];
    const newSelectedImageIds = [...selectedImageIds];

    for (let i = setIndex * 4; i < (setIndex + 1) * 4 && i < newSelectedImageIds.length; i++) {
      newSelectedImageIds[i] = false;
    }

    newSelectedImageIds[index] = true;
    newSelectedIndices[setIndex] = index % 4;

    setSelectedImageIds(newSelectedImageIds);
    setSelectedIndices(newSelectedIndices);
  };

  const isFormValid = () => {
    const validEmail = email.match(/^([\w.%+-]+)@([\w-]+\.)+([\w]{2,})$/i);
    const nameNotEmpty = username.trim() !== '';
    const eachSetHasSelection = selectedIndices.every(index => index !== -1);

    return nameNotEmpty && validEmail && eachSetHasSelection;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!isFormValid()) {
      setError('Please fill out all fields correctly before submitting.');
      return;
    }

    const submittedImageIds = surveyData.filter((id, index) => selectedImageIds[index]).map(id => id);
    console.log(submittedImageIds);

    const postData = {
      name: username,
      email: email,
      selected_image_ids: submittedImageIds
    };

    try {
      const response = await fetch(`${API_URL}/surveys/${id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(postData)
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      await response.json();
      window.alert('Response recorded successfully.');
      window.location.reload();
    } catch (error) {
      console.error('Failed to submit survey:', error);
      setError('Failed to submit survey. Please try again.');
    }
  };


  return (
    <div className="survey-container-fill">
      <form className="input-form" onSubmit={handleSubmit}>
        {error && <p className="error">{error}</p>}
        <div className="input-row">
          <input
            type="text"
            value={username}
            onChange={(e) => handleInputChange(e, setUsername)}
            placeholder="Enter your name"
          />
          <input
            type="email"
            value={email}
            onChange={(e) => handleInputChange(e, setEmail)}
            placeholder="Enter your email"
          />
        </div>
        <div className="image-grid">
          {surveyData.map((id, index) => {
            const setIndex = Math.floor(index / 4);
            return (
              <div key={index}
                   className={`image-item ${selectedIndices[setIndex] === index % 4 ? 'selected' : ''}`}
                   onClick={() => handleSelectImage(index)}>
                <img src={`/images/${id}.JPEG`}
                     onError={(e) => e.target.src = '/place holder.png'}
                     alt={`Survey Image ${id}`}
                />
                {/*<p>{id}</p>*/}
              </div>
            );
          })}
        </div>
        <button type="submit" className="submit-button" disabled={!isFormValid()}>Submit</button>
      </form>
    </div>
  );
}

export default Survey;
