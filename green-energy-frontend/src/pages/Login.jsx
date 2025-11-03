// src/pages/Login.jsx
import { useState } from "react";
import { Link } from "react-router-dom";
import AuthLayout from "../components/AuthLayout";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function handleSubmit(e) {
    e.preventDefault();
    setError("");

    // simple UI validation only
    if (!email || !password) {
      setError("Email and password are required.");
      return;
    }
    if (!/^\S+@\S+\.\S+$/.test(email)) {
      setError("Enter a valid email.");
      return;
    }

    // UI-only behaviour: we just simulate a request
    setLoading(true);
    setTimeout(() => {
      console.log("Login submitted (UI only)", { email, password });
      setLoading(false);
    }, 700);
  }

  return (
    <AuthLayout title="Welcome back!">
      <form onSubmit={handleSubmit}>
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

        <div className="auth-forgot">
          <button type="button" className="auth-link">
            Forgot password?
          </button>
        </div>

        {error && <p className="auth-error">{error}</p>}

        <button className="auth-button-primary" disabled={loading} type="submit">
          {loading ? "Logging in..." : "Login"}
        </button>
      </form>

      <div className="auth-footer">
        <span>Dont have an account?</span>
        <Link to="/register">Sign up</Link>
      </div>
    </AuthLayout>
  );
}
