
import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getToken } from "../services/authService";
import "./DeviceAnalytics.css";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

function DeviceAnalytics() {
  const { propertyId, deviceId } = useParams();
  const navigate = useNavigate();
  const [usage, setUsage] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchDeviceUsage() {
      const token = getToken();

      const response = await fetch(`${API_BASE_URL}/devices/${deviceId}/usage`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const data = await response.json();
      setUsage(data);
      setLoading(false);
    }

    fetchDeviceUsage();
  }, [deviceId]);

  if (loading) return <p>Loading device usage...</p>;

  return (
    <div className="device-container">
      <h2>Device Usage</h2>
      <p>Device Name: {usage.name}</p>
      <p>Total Usage: {usage.total_kwh} kWh</p>
      <p>Total Cost: £{usage.total_cost}</p>

      <button onClick={() => navigate(-1)} className="back-button">Back</button>
    </div>
  );
}

export default DeviceAnalytics;
