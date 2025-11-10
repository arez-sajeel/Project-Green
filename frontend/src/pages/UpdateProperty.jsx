import React, { useState } from "react";

export default function UpdateProperty() {
  const [formData, setFormData] = useState({
    name: "",
    address: "",
    type: "",
    rooms: "",
    tariff: "",
  });
  const [message, setMessage] = useState("");

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`http://127.0.0.1:8000/properties/1`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
        body: JSON.stringify(formData),
      });

      if (res.ok) {
        setMessage("✅ Property updated successfully!");
      } else {
        const err = await res.json();
        setMessage(`❌ Error: ${err.detail}`);
      }
    } catch (err) {
      console.error(err);
      setMessage("⚠️ Connection error. Please try again.");
    }
  };

  return (
    <div className="flex bg-gray-50 min-h-screen">
      <aside className="w-64 bg-green-800 text-white p-6">
        <h2 className="text-2xl font-bold mb-6">Property Manager</h2>
        <ul>
          <li className="py-2 hover:text-green-300 cursor-pointer">Dashboard</li>
          <li className="py-2 hover:text-green-300 cursor-pointer">Update Property</li>
        </ul>
      </aside>

      <main className="flex-1 p-10">
        <h1 className="text-3xl font-semibold text-green-800 mb-8">
          Update Property Details
        </h1>

        <form
          onSubmit={handleSubmit}
          className="bg-white p-8 rounded-2xl shadow-md max-w-2xl space-y-4"
        >
          {["name", "address", "type", "rooms", "tariff"].map((field) => (
            <div key={field}>
              <label
                htmlFor={field}
                className="block text-gray-700 capitalize mb-1"
              >
                {field}
              </label>
              <input
                id={field}
                name={field}
                value={formData[field]}
                onChange={handleChange}
                className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-green-700"
                required
              />
            </div>
          ))}
          <button
            type="submit"
            className="bg-green-700 hover:bg-green-800 text-white px-6 py-2 rounded-lg"
          >
            Save Changes
          </button>
        </form>

        {message && (
          <p className="mt-4 text-green-700 font-medium">{message}</p>
        )}
      </main>
    </div>
  );
}
