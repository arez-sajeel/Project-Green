// src/pages/SelectRole.jsx
import { useNavigate } from "react-router-dom";
import "./SelectRole.css";

export default function SelectRole() {
  const navigate = useNavigate();

  const handleSelect = async (role) => {
    try {
      // Update role in backend
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        // Not authenticated - redirect to login
        navigate("/login");
        return;
      }

      const response = await fetch('http://localhost:8000/auth/update-role', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ role })
      });

      if (!response.ok) {
        throw new Error('Failed to update role');
      }

      // Store the selected role in localStorage
      localStorage.setItem("userRole", role);
      
      // Navigate to appropriate dashboard based on role
      if (role === "Homeowner") {
        navigate("/homeowner-dashboard");
      } else if (role === "PropertyManager") {
        navigate("/manager-dashboard");
      }
      
    } catch (err) {
      console.error("Failed to update role:", err);
      // On error, clear auth and redirect to login
      localStorage.clear();
      navigate("/login");
    }
  };

  return (
    <div className="role-container">
      {/* Green curved header */}
      <div className="role-header"></div>

      {/* Main heading with pink/magenta color */}
      <h2 className="role-title">
        Choose the best option <br />
        for you to personalise <br />
        your experience
      </h2>

      {/* "Start profile" subtitle */}
      <p className="role-subtitle">Start profile</p>

      {/* Role selection cards */}
      <div className="role-card-group">
        {/* Homeowner card */}
        <div 
          className="role-card" 
          onClick={() => handleSelect("Homeowner")}
          role="button"
          tabIndex={0}
          onKeyPress={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              handleSelect("Homeowner");
            }
          }}
          aria-label="Select Homeowner role"
        >
          <div className="role-icon-wrapper">
            <svg className="role-icon" viewBox="0 0 100 100" fill="currentColor">
              <path d="M50 10 L90 40 L90 90 L60 90 L60 60 L40 60 L40 90 L10 90 L10 40 Z" />
              <circle cx="50" cy="50" r="5" fill="white" />
            </svg>
          </div>
          <p className="role-label">Homeowner</p>
        </div>

        {/* Property Manager card */}
        <div 
          className="role-card" 
          onClick={() => handleSelect("PropertyManager")}
          role="button"
          tabIndex={0}
          onKeyPress={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              handleSelect("PropertyManager");
            }
          }}
          aria-label="Select Property Manager role"
        >
          <div className="role-icon-wrapper">
            <svg className="role-icon" viewBox="0 0 100 100" fill="currentColor">
              <rect x="20" y="20" width="30" height="70" />
              <rect x="22" y="25" width="6" height="6" fill="white" />
              <rect x="32" y="25" width="6" height="6" fill="white" />
              <rect x="42" y="25" width="6" height="6" fill="white" />
              <rect x="22" y="35" width="6" height="6" fill="white" />
              <rect x="32" y="35" width="6" height="6" fill="white" />
              <rect x="42" y="35" width="6" height="6" fill="white" />
              <rect x="22" y="45" width="6" height="6" fill="white" />
              <rect x="32" y="45" width="6" height="6" fill="white" />
              <rect x="42" y="45" width="6" height="6" fill="white" />
              <rect x="55" y="40" width="25" height="50" />
              <rect x="57" y="45" width="5" height="5" fill="white" />
              <rect x="64" y="45" width="5" height="5" fill="white" />
              <rect x="71" y="45" width="5" height="5" fill="white" />
              <rect x="57" y="52" width="5" height="5" fill="white" />
              <rect x="64" y="52" width="5" height="5" fill="white" />
              <rect x="71" y="52" width="5" height="5" fill="white" />
            </svg>
          </div>
          <p className="role-label">Property<br />manager</p>
        </div>
      </div>

      {/* Login link at bottom */}
      <p className="role-login-text">
        Already have an account?{" "}
        <span className="role-login-link" onClick={() => navigate("/login")}>
          Login
        </span>
      </p>
    </div>
  );
}
