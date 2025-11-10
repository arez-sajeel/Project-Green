import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./HomeownerSetup.css";

export default function HomeownerSetup() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    propertyType: "",
    bedrooms: 1,
    heatingType: "",
    tariffType: "",
    monthlyBill: "",
    solar: false,
  });

  const handleChange = (field, value) => {
    setForm({ ...form, [field]: value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Later this will POST to backend
    navigate("/homeowner-dashboard");
  };

  return (
    <div className="setup-container">
      <div className="setup-header">
        <h1 className="setup-title">Tell us about your property</h1>
      </div>

      <form className="setup-form" onSubmit={handleSubmit}>
        
        <label>Property type</label>
        <select
          value={form.propertyType}
          onChange={(e) => handleChange("propertyType", e.target.value)}
        >
          <option></option>
          <option>House</option>
          <option>Flat</option>
        </select>

        <label>How many bedrooms?</label>
        <input
          type="number"
          min="1"
          value={form.bedrooms}
          onChange={(e) => handleChange("bedrooms", e.target.value)}
        />

        <label>Heating type</label>
        <select
          value={form.heatingType}
          onChange={(e) => handleChange("heatingType", e.target.value)}
        >
          <option></option>
          <option>Gas</option>
          <option>Electric</option>
          <option>Oil</option>
        </select>

        <label>Tariff type</label>
        <select
          value={form.tariffType}
          onChange={(e) => handleChange("tariffType", e.target.value)}
        >
          <option></option>
          <option>Standard</option>
          <option>Economy 7</option>
        </select>

        <label>Average monthly bill (£)</label>
        <input
          type="number"
          value={form.monthlyBill}
          onChange={(e) => handleChange("monthlyBill", e.target.value)}
        />

        <label className="toggle-row">
          Solar panels
          <input
            type="checkbox"
            checked={form.solar}
            onChange={() => handleChange("solar", !form.solar)}
          />
        </label>

        <button className="setup-continue-btn">Continue</button>
      </form>
    </div>
  );
}
