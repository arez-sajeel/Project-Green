import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./PropertyManagerSetup.css";

export default function PropertyManagerSetup() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    propertyCount: 1,
    propertyType: "",
    avgOccupancy: "",
    maintenanceCost: "",
    budgetGoal: "",
  });

  const handleChange = (field, value) => {
    setForm({ ...form, [field]: value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Later this will send to backend
    navigate("/manager-dashboard");
  };

  return (
    <div className="pm-setup-container">
      <div className="pm-setup-header">
        <h1 className="pm-setup-title">Tell us about your properties</h1>
      </div>

      <form className="pm-setup-form" onSubmit={handleSubmit}>

        <label>Number of properties</label>
        <input
          type="range"
          min="1"
          max="100"
          value={form.propertyCount}
          onChange={(e) => handleChange("propertyCount", e.target.value)}
        />
        <span className="pm-range-value">{form.propertyCount}</span>

        <label>Property type</label>
        <select
          value={form.propertyType}
          onChange={(e) => handleChange("propertyType", e.target.value)}
        >
          <option></option>
          <option>Residential</option>
          <option>Commercial</option>
          <option>Mixed-use</option>
        </select>

        <label>Average occupancy (%)</label>
        <input
          type="number"
          min="0"
          max="100"
          value={form.avgOccupancy}
          onChange={(e) => handleChange("avgOccupancy", e.target.value)}
        />

        <label>Monthly maintenance cost (£)</label>
        <input
          type="number"
          value={form.maintenanceCost}
          onChange={(e) => handleChange("maintenanceCost", e.target.value)}
        />

        <label>Budget savings goal (£)</label>
        <input
          type="number"
          value={form.budgetGoal}
          onChange={(e) => handleChange("budgetGoal", e.target.value)}
        />

        <button className="pm-continue-btn">Continue</button>
      </form>
    </div>
  );
}
