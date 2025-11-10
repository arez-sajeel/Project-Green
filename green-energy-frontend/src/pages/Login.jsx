// src/pages/Login.jsx
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import AuthLayout from "../components/AuthLayout";
import { loginUser, saveToken } from "../services/authService";

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
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

    // Connect to backend
    setLoading(true);
    try {
      const data = await loginUser(email, password);

      // Save the JWT token
      saveToken(data.access_token);

      // Check if user has completed role selection
      // The backend should return user info including role
      // For now, we'll check after login by fetching user profile
      
      // Clear form
      setEmail("");
      setPassword("");
      setError("");

      // Check user's role from backend
      await checkUserRole();

    } catch (err) {
      setError(err.message || "Login failed. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  async function checkUserRole() {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const userData = await response.json();
        
        if (!userData.role || userData.role === null) {
          // User has no role - redirect to role selection
          navigate("/role");
        } else {
          // User has a role - store it and redirect to appropriate dashboard
          localStorage.setItem("userRole", userData.role);
          
          if (userData.role === "Homeowner") {
            navigate("/homeowner-dashboard");
          } else if (userData.role === "PropertyManager") {
            navigate("/manager-dashboard");
          }
        }
      }
    } catch (err) {
      console.error("Failed to fetch user role:", err);
      // On error, redirect to role selection to be safe
      navigate("/role");
    }
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
        <span>Dont have an account? </span>
        <Link to="/register">Sign up</Link>
      </div>
    </AuthLayout>
  );
}

