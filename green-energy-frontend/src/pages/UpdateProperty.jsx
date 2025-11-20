import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getToken } from "../services/authService";
import "./UpdateProperty.css";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

function UpdateProperty() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [formData, setFormData] = useState({
    address: "",
    location: "",
    sq_footage: "",
    tariff_id: "",
    portfolio_id: "",
    mpan_id: "",
  });

  useEffect(() => {
    async function fetchProperty() {
      try {
        const token = getToken();
        const response = await fetch(`${API_BASE_URL}/properties/${id}`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (!response.ok) throw new Error("Failed to load property");

        const data = await response.json();

        setFormData({
          address: data.address || "",
          location: data.location || "",
          sq_footage: data.sq_footage || "",
          tariff_id: data.tariff_id || "",
          portfolio_id: data.portfolio_id || "",
          mpan_id: data.mpan_id || "",
        });
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchProperty();
  }, [id]);

  function handleChange(e) {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setSaving(true);
    setError("");
    setSuccess("");

    try {
      const token = getToken();
      const response = await fetch(`${API_BASE_URL}/properties/${id}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || "Failed to update property");
      }

      setSuccess("Property updated successfully!");
      setTimeout(() => navigate("/manager-dashboard"), 1200);
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <p>Loading property…</p>;

  return (
    <div className="form-container">
      <h2>Update Property</h2>

      {error && <p className="error-message">{error}</p>}
      {success && <p className="success-message">{success}</p>}

      <form onSubmit={handleSubmit}>
        <label>Address:
          <input type="text" name="address" value={formData.address}
           onChange={handleChange} required />
        </label>

        <label>Location:
          <input type="text" name="location" value={formData.location}
           onChange={handleChange} required />
        </label>

        <label>Sq. Footage:
          <input type="number" name="sq_footage" value={formData.sq_footage}
           onChange={handleChange} required />
        </label>

        <label>Tariff ID:
          <input type="number" name="tariff_id" value={formData.tariff_id}
           onChange={handleChange} required />
        </label>

        <label>Portfolio ID:
          <input type="number" name="portfolio_id" value={formData.portfolio_id}
           onChange={handleChange} required />
        </label>

        <label>MPAN ID:
          <input type="text" name="mpan_id" value={formData.mpan_id}
           onChange={handleChange} />
        </label>

        <button type="submit" disabled={saving}>
          {saving ? "Saving…" : "Save Changes"}
        </button>
      </form>

      <button onClick={() => navigate("/manager-dashboard")}
       className="back-button">
        Back to Dashboard
      </button>
    </div>
  );
}

export default UpdateProperty;
