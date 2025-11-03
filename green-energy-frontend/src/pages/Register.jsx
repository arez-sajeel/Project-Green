// src/pages/Register.jsx
import { useState } from "react";
import { Link } from "react-router-dom";
import AuthLayout from "../components/AuthLayout";

export default function Register() {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function handleSubmit(e) {
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

    // UI-only: pretend to send request
    setLoading(true);
    setTimeout(() => {
      console.log("Register submitted (UI only)", {
        fullName,
        email,
        password,
      });
      setLoading(false);
    }, 700);
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
          {loading ? "Creating..." : "Login"}
          {/* If you want the button text to be "Sign up" instead, change here */}
        </button>
      </form>

      <div className="auth-footer">
        <span>Already have an account?</span>
        <Link to="/login">Login</Link>
      </div>
    </AuthLayout>
  );
}
