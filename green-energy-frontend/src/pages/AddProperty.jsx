import React, { useState } from "react";
import axios from "axios";

const AddProperty = () => {
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

  const validate = (name, value) => {
    let msg = "";
    if (name === "property_type" && value.trim().length < 2) msg = "Enter a valid property type";
    if (name === "location" && value.trim().length < 2) msg = "Enter a valid location";
    if (name === "average_monthly_kwh" && value < 0) msg = "Invalid value";
    return msg;
  };

  const updateField = (e) => {
    const { name, value, type, checked } = e.target;
    const newValue = type === "checkbox" ? checked : value;

    setForm((prev) => ({ ...prev, [name]: newValue }));

    setErrors((prev) => ({
      ...prev,
      [name]: validate(name, newValue),
    }));
  };

  const handleSubmit = async () => {
    const hasErrors = Object.values(errors).some((e) => e);

    if (hasErrors) {
      setSuccess("");
      return;
    }

    try {
      const res = await axios.post("http://localhost:8000/add-property", form);
      setSuccess("Property added successfully!");
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Tell us about your property</h2>

      <div style={styles.formGroup}>
        <label>Property Type</label>
        <input
          type="text"
          name="property_type"
          value={form.property_type}
          onChange={updateField}
          style={styles.input}
        />
        {errors.property_type && <p style={styles.error}>{errors.property_type}</p>}
      </div>

      <div style={styles.formGroup}>
        <label>Location</label>
        <input
          type="text"
          name="location"
          value={form.location}
          onChange={updateField}
          style={styles.input}
        />
        {errors.location && <p style={styles.error}>{errors.location}</p>}
      </div>

      <div style={styles.formGroup}>
        <label>Tariff Type</label>
        <select
          name="tariff_type"
          value={form.tariff_type}
          onChange={updateField}
          style={styles.select}
        >
          <option value="">Select a tariff</option>
          <option value="Standing Charge">Standing Charge</option>
          <option value="Tariff 2">Tariff 2</option>
        </select>
      </div>

      <div style={styles.formGroup}>
        <label>Average Monthly kWh</label>
        <input
          type="number"
          name="average_monthly_kwh"
          value={form.average_monthly_kwh}
          onChange={updateField}
          style={styles.input}
        />
      </div>

      <div style={styles.switchRow}>
        <label>Solar Panels</label>
        <input
          type="checkbox"
          name="solar_panels"
          checked={form.solar_panels}
          onChange={updateField}
        />
      </div>

      <div style={styles.formGroup}>
        <label>Occupancy</label>
        <input
          type="number"
          name="occupancy"
          value={form.occupancy}
          onChange={updateField}
          style={styles.input}
        />
      </div>

      <div style={styles.formGroup}>
        <label>Maintenance Cost</label>
        <input
          type="number"
          name="maintenance_cost"
          value={form.maintenance_cost}
          onChange={updateField}
          style={styles.input}
        />
      </div>

      <div style={styles.formGroup}>
        <label>Budget</label>
        <input
          type="number"
          name="budget"
          value={form.budget}
          onChange={updateField}
          style={styles.input}
        />
      </div>

      <div style={styles.formGroup}>
        <label>Carbon Goal</label>
        <select
          name="carbon_goal"
          value={form.carbon_goal}
          onChange={updateField}
          style={styles.select}
        >
          <option value="">Select goal</option>
          <option value="Reduce">Reduce</option>
          <option value="Neutral">Neutral</option>
        </select>
      </div>

      <button style={styles.button} onClick={handleSubmit}>Continue</button>

      {success && <p style={styles.success}>{success}</p>}
    </div>
  );
};

export default AddProperty;

const styles = {
  container: {
    padding: "20px",
    maxWidth: "400px",
    margin: "auto",
    background: "#f5ffe6",
    borderRadius: "12px",
  },
  title: {
    color: "#0b7d12",
    marginBottom: "20px",
    textAlign: "center",
  },
  formGroup: {
    marginBottom: "15px",
  },
  input: {
    width: "100%",
    padding: "10px",
    borderRadius: "10px",
    border: "1px solid #cfcfcf",
  },
  select: {
    width: "100%",
    padding: "10px",
    borderRadius: "10px",
    border: "1px solid #cfcfcf",
  },
  switchRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "15px",
  },
  button: {
    width: "100%",
    backgroundColor: "#ff1fa0",
    padding: "12px",
    borderRadius: "10px",
    border: "none",
    color: "white",
    fontSize: "18px",
    marginTop: "10px",
    cursor: "pointer",
  },
  error: {
    color: "red",
    fontSize: "12px",
  },
  success: {
    color: "green",
    marginTop: "10px",
    textAlign: "center",
  },
};
