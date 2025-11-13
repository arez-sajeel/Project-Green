import { useNavigate } from "react-router-dom";
import "./PropertyManagerDashboard.css";

export default function PropertyManagerDashboard() {
  const navigate = useNavigate();
  const role = localStorage.getItem("userRole") || "property_manager";

  const handleLogout = () => {
    localStorage.clear();
    navigate("/login");
  };

  return (
    <div className="pm-dash-container">

      {/* HEADER */}
      <div className="pm-dash-header">
        <h1>Property Manager Dashboard 🏢</h1>
        <p>Logged in as <strong>{role}</strong></p>
      </div>

      {/* CARDS */}
      <div className="pm-dash-grid">

        <div className="pm-dash-card">
          <h3>View Properties</h3>
          <p>See a list of all your managed properties.</p>
          <button>Open Properties</button>
        </div>

        <div className="pm-dash-card">
          <h3>Energy Efficiency Reports</h3>
          <p>Compare energy usage and performance across buildings.</p>
          <button>View Reports</button>
        </div>

        <div className="pm-dash-card">
          <h3>Cost Reduction Insights</h3>
          <p>Get suggestions to lower operating costs and energy waste.</p>
          <button>View Insights</button>
        </div>

      </div>

      {/* LOGOUT */}
      <button className="pm-dash-logout" onClick={handleLogout}>
        Logout
      </button>
    </div>
  );
}
