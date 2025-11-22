
import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getToken } from "../services/authService";
import "./UsageLogsViewer.css";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

function UsageLogsViewer() {
  const { id } = useParams(); // property ID
  const navigate = useNavigate();

  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [sortOrder, setSortOrder] = useState("desc");

  useEffect(() => {
    async function fetchLogs() {
      try {
        const token = getToken();
        const response = await fetch(`${API_BASE_URL}/properties/${id}/usage`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error("Failed to load usage logs");
        }

        const data = await response.json();
        setLogs(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchLogs();
  }, [id]);

  function toggleSort() {
    const sorted = [...logs].sort((a, b) =>
      sortOrder === "asc"
        ? new Date(b.timestamp) - new Date(a.timestamp)
        : new Date(a.timestamp) - new Date(b.timestamp)
    );
    setLogs(sorted);
    setSortOrder(sortOrder === "asc" ? "desc" : "asc");
  }

  if (loading) return <p>Loading logs…</p>;

  return (
    <div className="usage-container">
      <h2>Usage Logs</h2>

      {error && <p className="error-message">{error}</p>}

      <button onClick={toggleSort} className="sort-button">
        Sort by Date ({sortOrder === "asc" ? "Oldest" : "Newest"})
      </button>

      {logs.length === 0 ? (
        <p>No usage logs found.</p>
      ) : (
        <table className="usage-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>kWh</th>
              <th>Cost (£)</th>
              <th>Source</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log, index) => (
              <tr key={index}>
                <td>{new Date(log.timestamp).toLocaleString()}</td>
                <td>{log.kwh_consumption}</td>
                <td>{log.kwh_cost}</td>
                <td>{log.reading_type}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <button onClick={() => navigate(-1)} className="back-button">
        Back to Property
      </button>
    </div>
  );
}

export default UsageLogsViewer;
