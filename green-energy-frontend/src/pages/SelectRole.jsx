// src/pages/SelectRole.jsx
import { useNavigate } from "react-router-dom";
import "./SelectRole.css";

export default function SelectRole() {
  const navigate = useNavigate();

  const handleSelect = (role) => {
    localStorage.setItem("userRole", role);
    navigate("/register");
  };

  return (
    <div className="role-container">
      <div className="role-header"></div>

      <h2 className="role-title">
        Choose the best option <br />
        for you to personalise your experience
      </h2>

      <p className="role-subtitle">Start profile</p>

      <div className="role-card-group">
        <div className="role-card" onClick={() => handleSelect("homeowner")}>
          <img src="/home-icon.svg" alt="Homeowner" className="role-icon" />
          <p className="role-label">Homeowner</p>
        </div>

        <div className="role-card" onClick={() => handleSelect("property_manager")}>
          <img src="/building-icon.svg" alt="Property Manager" className="role-icon" />
          <p className="role-label">Property manager</p>
        </div>
      </div>

      <p className="role-login-text">
        Already have an account?{" "}
        <span className="role-login-link" onClick={() => navigate("/login")}>
          Login
        </span>
      </p>
    </div>
  );
}
