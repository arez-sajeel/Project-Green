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

    setLoading(true);

    // Register user without a role - they must select it on the next page
    try {
      const response = await fetch('http://localhost:8000/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          password,
          // Don't include role - user must select on role page
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        // If email exists, show error and don't proceed
        if (response.status === 409) {
          setError("A user with this email already exists.");
          setLoading(false);
          return;
        }
        setError(errorData.detail || "Registration failed. Please try again.");
        setLoading(false);
        return;
      }

      // Registration successful - store token and redirect to role selection
      const data = await response.json();
      saveToken(data.access_token);
      
      // Clear form fields
      setEmail("");
      setPassword("");
      setFullName("");
      
      // Redirect to role selection - user MUST select a role to continue
      navigate("/role");
      
    } catch (err) {
      setError("Registration failed. Please try again.");
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
