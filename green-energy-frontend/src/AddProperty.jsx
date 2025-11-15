import { useState } from "react";
import axios from "axios";

export default function AddProperty() {
  const [form, setForm] = useState({
    property_type: "",
    location: "",
    tariff_type: "",
    average_monthly_kwh: "",
    solar_panels: false,
    occupancy: "",
    maintenance_cost: "",
    budget: "",
    carbon_goal: "",
  });

  const [errors, setErrors] = useState({});
  const [success, setSuccess] = useState("");

  // -----------------------
  // Live Validation Function
  // -----------------------
  const validateField = (name, value) => {
    let message = "";

    if (name === "property_type" && value.trim().length < 2) {
      message = "Property type is required.";
    }

    if (name === "location" && value.trim().length < 2) {
      message = "Location is required.";
    }

    if (
      [
        "average_monthly_kwh",
        "occupancy",
        "maintenance_cost",
        "budget",
      ].includes(name)
    ) {
      if (value !== "" && value < 0) message = "Value must be positive.";
    }

    return message;
  };

  // -----------------------
  // Update field + live validation
  // -----------------------
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    const newValue = type === "checkbox" ? checked : value;

    setForm((prev) => ({ ...prev, [name]: newValue }));

    setErrors((prev) => ({
      ...prev,
      [name]: validateField(name, newValue),
    }));
  };

  // -----------------------
  // Submit form to backend
  // -----------------------
  const handleSubmit = async () => {
    // Check client-side validation
    const hasErrors = Object.values(errors).some((msg) => msg && msg !== "");

    if (hasErrors) {
      alert("Please fix errors before submitting.");
      return;
    }

    try {
      const response = await axios.post(
        "http://localhost:8000/properties/add",
        form
      );

      console.log("Saved:", response.data);
      setSuccess("Property added successfully!");

      // Reset form for adding more properties
      setForm({
        property_type: "",
        location: "",
        tariff_type: "",
        average_monthly_kwh: "",
        solar_panels: false,
        occupancy: "",
        maintenance_cost: "",
        budget: "",
        carbon_goal: "",
      });

      setErrors({});
    } catch (error) {
      console.error("Error saving property:", error);
      alert("Error saving property.");
    }
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Add Property</h2>

      {/* Property Type */}
      <label style={styles.label}>Property Type</label>
      <input
        style={styles.input}
        name="property_type"
        value={form.property_type}
        onChange={handleChange}
      />
      {errors.property_type && (
        <p style={styles.error}>{errors.property_type}</p>
      )}

      {/* Location */}
      <label style={styles.label}>Location</label>
      <input
        style={styles.input}
        name="location"
        value={form.location}
        onChange={handleChange}
      />
      {errors.location && <p style={styles.error}>{errors.location}</p>}

      {/* Tariff Type */}
      <label style={styles.label}>Tariff Type</label>
      <select
        style={styles.input}
        name="tariff_type"
        value={form.tariff_type}
        onChange={handleChange}
      >
        <option value="">Select</option>
        <option value="Fixed">Fixed</option>
        <option value="Variable">Variable</option>
      </select>

      {/* Monthly kWh */}
      <label style={styles.label}>Average Monthly kWh</label>
      <input
        type="number"
        style={styles.input}
        name="average_monthly_kwh"
        value={form.average_monthly_kwh}
        onChange={handleChange}
      />

      {/* Solar Panels */}
      <label style={{ ...styles.label, marginTop: "10px" }}>
        <input
          type="checkbox"
          name="solar_panels"
          checked={form.solar_panels}
          onChange={handleChange}
        />
        &nbsp; Solar Panels
      </label>

      {/* Occupancy */}
      <label style={styles.label}>Occupancy</label>
      <input
        type="number"
        style={styles.input}
        name="occupancy"
        value={form.occupancy}
        onChange={handleChange}
      />

      {/* Maintenance Cost */}
      <label style={styles.label}>Maintenance Cost (£)</label>
      <input
        type="number"
        style={styles.input}
        name="maintenance_cost"
        value={form.maintenance_cost}
        onChange={handleChange}
      />

      {/* Budget */}
      <label style={styles.label}>Budget (£)</label>
      <input
        type="number"
        style={styles.input}
        name="budget"
        value={form.budget}
        onChange={handleChange}
      />

      {/* Carbon Goal */}
      <label style={styles.label}>Carbon Goal</label>
      <select
        style={styles.input}
        name="carbon_goal"
        value={form.carbon_goal}
        onChange={handleChange}
      >
        <option value="">Select</option>
        <option value="Reduce">Reduce only</option>
        <option value="Neutral">Carbon Neutral</option>
      </select>

      {/* Submit */}
      <button style={styles.button} onClick={handleSubmit}>
        Add Property
      </button>

      {success && <p style={styles.success}>{success}</p>}
    </div>
  );
}

const styles = {
  container: {
    maxWidth: "400px",
    margin: "auto",
    padding: "20px",
    borderRadius: "12px",
    backgroundColor: "#f4ffe6",
  },
  title: {
    textAlign: "center",
    color: "#008000",
    marginBottom: "20px",
  },
  label: {
    marginTop: "10px",
    fontWeight: "bold",
  },
  input: {
    width: "100%",
    padding: "10px",
    borderRadius: "8px",
    border: "1px solid #ccc",
    marginTop: "5px",
  },
  button: {
    width: "100%",
    backgroundColor: "#ff1fa0",
    padding: "12px",
    borderRadius: "10px",
    border: "none",
    color: "white",
    fontSize: "18px",
    cursor: "pointer",
    marginTop: "20px",
  },
  error: {
    fontSize: "12px",
    color: "red",
  },
  success: {
    color: "green",
    textAlign: "center",
    marginTop: "15px",
  },
};
