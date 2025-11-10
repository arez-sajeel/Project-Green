<<<<<<< Updated upstream
// src/App.jsx
import { Routes, Route, Navigate } from "react-router-dom";
=======
import { Routes, Route } from "react-router-dom";
import Welcome from "./pages/Welcome.jsx";
>>>>>>> Stashed changes
import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";

<<<<<<< Updated upstream
function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" replace />} />
=======
/**
 * App Component - Main Application Router
 * Sprint 1: Core Architecture & Access (Foundation)
 * 
 * Implements complete Sprint 1 requirements:
 * - Task 2: Welcome Page (Landing screen with Renewi branding)
 * - Task 3: Login Page 
 * - Task 4: Create Account Page
 * - Task 5: Role-Based Access Setup
 * - Protected routes based on user role
 */
function App() {
  return (
    <Routes>
      {/* Sprint 1 Task 2: Welcome Page - Landing page */}
      <Route path="/" element={<Welcome />} />
      
      {/* Authentication routes */}
>>>>>>> Stashed changes
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
    </Routes>
  );
}

export default App;
