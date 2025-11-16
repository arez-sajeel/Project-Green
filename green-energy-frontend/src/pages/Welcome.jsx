import React from 'react';
import { useNavigate } from 'react-router-dom';
import './Welcome.css';

const WelcomePage = () => {
  const navigate = useNavigate();

  return (
    <div className="welcome-root">
      <div className="welcome-card auth-card">
        <div className="welcome-content auth-body">
          <header>
            <h1 className="welcome-title">Renewi</h1>
            <p className="welcome-tagline">An apple a day keeps the power bills away.</p>
          </header>

          <div className="welcome-buttons">
            <button
              type="button"
              className="welcome-button welcome-button-login"
              onClick={() => navigate('/login')}
            >
              Login
            </button>

            <button
              type="button"
              className="welcome-button welcome-button-signup"
              onClick={() => navigate('/register')}
            >
              Sign Up
            </button>
          </div>

          <div className="welcome-mascot-container">
            <img
              src="/renewi-logo.png"
              alt="Renewi mascot waving"
              className="welcome-mascot"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default WelcomePage;