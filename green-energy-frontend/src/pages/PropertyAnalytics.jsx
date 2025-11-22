
import { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { getToken } from "../services/authService";
import "./PropertyAnalytics.css";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

function PropertyAnalytics() {
  const { propertyId } = useParams();
  const navigate = useNavigate();
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchAnalytics() {
      const token = getToken();

      const response = await fetch(`${API_BASE_URL}/properties/${propertyId}/analytics`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const data = await response.json();
      setAnalytics(data);
      setLoading(false);
    }

    fetchAnalytics();
  }, [propertyId]);

  if (loading) return <p>Loading analytics...</p>;

  return (
    <div className="analytics-container">
      <h2>Property Analytics</h2>
      <p>Total Usage: {analytics.total_kwh} kWh</p>
      <p>Total Cost: £{analytics.total_cost}</p>

      <h3>Devices</h3>
      <ul>
        {analytics.devices.map((device) => (
          <li key={device.id}>
            <Link to={`/manager/property/${propertyId}/device/${device.id}`}>
              {device.name} - {device.kwh} kWh
            </Link>
          </li>
        ))}
      </ul>

      <button onClick={() => navigate(-1)} className="back-button">Back</button>
    </div>
  );
}

export default PropertyAnalytics;
