import { useNavigate } from "react-router-dom";
import "./HomeownerDashboard.css";

export default function HomeownerDashboard() {
  const navigate = useNavigate();
  const role = localStorage.getItem("userRole") || "homeowner";

  const handleLogout = () => {
    localStorage.clear();
    navigate("/login");
  };

  return (
    <div className="hd-container">
      {/* HEADER */}
      <div className="hd-header">
        <h1>Welcome back 👋</h1>
        <p>You are logged in as a <strong>{role}</strong></p>
      </div>

      {/* DASHBOARD CARDS */}
      <div className="hd-card-grid">

        <div className="hd-card">
          <h3>Your Energy Usage</h3>
          <p>Track how much energy your home consumes throughout the day.</p>
          <button>View Usage</button>
        </div>

        <div className="hd-card">
          <h3>Smart Recommendations</h3>
          <p>See personalised suggestions on how to reduce energy waste.</p>
          <button>View Recommendations</button>
        </div>

        <div className="hd-card">
          <h3>Estimated Savings</h3>
          <p>View your financial + carbon impact savings predictions.</p>
          <button>View Savings</button>
        </div>

      </div>

      {/* LOGOUT */}
      <button className="hd-logout" onClick={handleLogout}>
        Logout
      </button>
    </div>
  );
}
