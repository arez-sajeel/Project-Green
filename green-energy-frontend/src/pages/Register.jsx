// src/pages/Register.jsx
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import AuthLayout from "../components/AuthLayout";
import { registerUser, saveToken } from "../services/authService";

export default function Register() {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    if (!fullName || !email || !password) {
      setError("All fields are required.");
      return;
    }
    if (!/^\S+@\S+\.\S+$/.test(email)) {
      setError("Enter a valid email.");
      return;
    }

    // Connect to backend
    setLoading(true);
    try {
      // Default to Homeowner role for now
      const data = await registerUser(email, password, "Homeowner");
      
      // Save the JWT token
      saveToken(data.access_token);
      
      // Redirect to homeowner dashboard
      console.log("Registration successful!", data);
      navigate("/homeowner");
      
    } catch (err) {
      setError(err.message || "Registration failed. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthLayout title="Create an account!">
      <form onSubmit={handleSubmit}>
        <label className="auth-field-label">Full name:</label>
        <input
          className="auth-input"
          type="text"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          placeholder="Full name"
        />

        <label className="auth-field-label">Email:</label>
        <input
          className="auth-input"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email"
        />

        <label className="auth-field-label">Password:</label>
        <input
          className="auth-input"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
        />

        {error && <p className="auth-error">{error}</p>}

        <button className="auth-button-primary" disabled={loading} type="submit">
          {loading ? "Creating..." : "Sign up"}
        </button>
      </form>

      <div className="auth-footer">
        <span>Already have an account?</span>
        <Link to="/login">Login</Link>
      </div>
    </AuthLayout>
  );
}
