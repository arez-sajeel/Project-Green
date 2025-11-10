import { Routes, Route, Navigate } from "react-router-dom";
import Welcome from "./pages/Welcome.jsx"; // New Welcome Page import
import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";
import SelectRole from "./pages/SelectRole.jsx";
import HomeownerSetup from "./pages/HomeownerSetup.jsx";
import PropertyManagerSetup from "./pages/PropertyManagerSetup.jsx";
import HomeownerDashboard from "./pages/HomeownerDashboard.jsx";
import PropertyManagerDashboard from "./pages/PropertyManagerDashboard.jsx";
import RoleProtectedRoute from "./components/RoleProtectedRoute.jsx";

/**
 * App Component - Main Application Router
 * Sprint 1: Core Architecture & Access (Foundation)
 * * Implements complete Sprint 1 requirements:
 * - Task 2: Welcome Page (Landing screen with Renewi branding)
 * - Task 3: Login Page 
 * - Task 4: Create Account Page
 * - Task 5: Role-Based Access Setup
 * - Protected routes based on user role
 */
function App() {
  return (
    <Routes>
      {/* Root Path: Now points to the Welcome page */}
      <Route path="/" element={<Welcome />} />
      
      {/* Authentication routes */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      
      {/* Role selection page (Sprint 1.5) */}
      <Route path="/role" element={<SelectRole />} />
      
      {/* Homeowner routes */}
      <Route 
        path="/homeowner-setup" 
        element={
          <RoleProtectedRoute allowedRole="Homeowner">
            <HomeownerSetup />
          </RoleProtectedRoute>
        } 
      />
      <Route 
        path="/homeowner-dashboard" 
        element={
          <RoleProtectedRoute allowedRole="Homeowner">
            <HomeownerDashboard />
          </RoleProtectedRoute>
        } 
      />
      
      {/* Property Manager routes */}
      <Route 
        path="/manager-setup" 
        element={
          <RoleProtectedRoute allowedRole="PropertyManager">
            <PropertyManagerSetup />
          </RoleProtectedRoute>
        } 
      />
      <Route 
        path="/manager-dashboard" 
        element={
          <RoleProtectedRoute allowedRole="PropertyManager">
            <PropertyManagerDashboard />
          </RoleProtectedRoute>
        } 
      />
    </Routes>
  );
}

export default App;