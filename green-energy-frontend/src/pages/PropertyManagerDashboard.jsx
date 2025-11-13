
import { useEffect, useState } from "react";
import { fetchUserContext, addProperty } from "../services/propertyService";
import "./PropertyManagerDashboard.css";

export default function PropertyManagerDashboard() {
  const [properties, setProperties] = useState([]);
  const [loading, setLoading] = useState(true);

  // new property form
  const [propertyId, setPropertyId] = useState("");
  const [providerCode, setProviderCode] = useState("");

  // validation state
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);

  // Load all properties from backend
  useEffect(() => {
    async function load() {
      try {
        const data = await fetchUserContext();
        setProperties(data.properties || []);
      } catch (err) {
        console.error("Error loading properties:", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  // Live validation
  function validate() {
    let newErrors = {};

    if (!propertyId.trim()) {
      newErrors.propertyId = "Property ID is required";
    } else if (propertyId.length < 4) {
      newErrors.propertyId = "Too short — must be at least 4 characters";
    }

    if (!providerCode.trim()) {
      newErrors.providerCode = "Provider code is required";
    } else if (!/^[A-Za-z0-9]+$/.test(providerCode)) {
      newErrors.providerCode = "Provider code must be alphanumeric";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!validate()) return;

    setSubmitting(true);

    try {
      const newProperty = await addProperty(propertyId, providerCode);

      // update list without reload
      setProperties((prev) => [...prev, newProperty]);

      setPropertyId("");
      setProviderCode("");
      setErrors({});
    } catch (err) {
      console.error("Add property error:", err);
      setErrors({ submit: err.message || "Could not add property" });
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="pm-container">

      {/* HEADER */}
      <div className="pm-header">Properties</div>

      {/* EXISTING PROPERTIES LIST */}
      <div className="pm-section">
        <h3>Your Properties</h3>

        {loading ? (
          <p>Loading...</p>
        ) : properties.length === 0 ? (
          <p>No properties found.</p>
        ) : (
          <div className="pm-prop-list">
            {properties.map((p) => (
              <div key={p.property_id} className="pm-prop-card">
                <div className="pm-prop-icon">{p.shortcode || "🏠"}</div>
                <div className="pm-prop-text">
                  <strong>{p.name}</strong>
                  <small>{p.energy_usage || "0.0 kWh"}</small>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ADD NEW PROPERTY FORM */}
      <div className="pm-section">
        <h3>Add a new property</h3>

        <form onSubmit={handleSubmit} className="pm-form">
          <label>Property ID</label>
          <input
            type="text"
            value={propertyId}
            onChange={(e) => setPropertyId(e.target.value)}
            onBlur={validate}
          />
          {errors.propertyId && <p className="pm-error">{errors.propertyId}</p>}

          <label>Provider Code</label>
          <input
            type="text"
            value={providerCode}
            onChange={(e) => setProviderCode(e.target.value)}
            onBlur={validate}
          />
          {errors.providerCode && (
            <p className="pm-error">{errors.providerCode}</p>
          )}

          {errors.submit && <p className="pm-error">{errors.submit}</p>}

          <button disabled={submitting} className="pm-btn">
            {submitting ? "Adding..." : "Submit"}
          </button>
        </form>

        <button className="pm-connect-btn">Connect Property</button>
      </div>
    </div>
  );
}
