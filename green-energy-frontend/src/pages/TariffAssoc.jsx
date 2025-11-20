import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./App.css";

export default function TariffAssociationPage(){
    const navigate = useNavigate();

    const [form, setForm] = useState({
        propertyName: "",
        propertyType: "",
        tariffPlanId: "",
    });

    const tariffPlans = [
        { id: 1, name: "Standard Tariff" },
        { id: 2, name: "Peak / Off-Peak" },
        { id: 3, name: "Green Energy Tariff" }
    ]
    const handleChange = (field, value) => {
setForm({ ...form, [field]: value });
};


const handleSubmit = (e) => {
e.preventDefault();


console.log("Tariff association submitted:", form);
navigate("/manager-dashboard");
};


return (
<div className="pm-setup-container">
<div className="pm-setup-header">
<h1 className="pm-setup-title">Assign a Tariff Plan</h1>
</div>


<form className="pm-setup-form" onSubmit={handleSubmit}>
<label>Property Name</label>
<input
type="text"
value={form.propertyName}
onChange={(e) => handleChange("propertyName", e.target.value)}
/>


<label>Property Type</label>
<select
value={form.propertyType}
onChange={(e) => handleChange("propertyType", e.target.value)}
>
<option value=""></option>
<option>Residential</option>
<option>Commercial</option>
<option>Mixed-use</option>
</select>


<label>Select Tariff Plan</label>
<select
value={form.tariffPlanId}
onChange={(e) => handleChange("tariffPlanId", e.target.value)}
>
<option value="">Choose a tariff</option>
{tariffPlans.map((plan) => (
<option key={plan.id} value={plan.id}>
{plan.name}
</option>
))}
</select>


<button className="pm-continue-btn">Save Tariff Selection</button>
</form>
</div>
);
}