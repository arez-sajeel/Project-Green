import { Routes, Route, Navigate } from "react-router-dom";
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
 * Sprint 1.5: Role-Based Access Setup
 * 
 * Implements role-based routing logic:
 * - Role selection page
 * - Login and Register functionality
 * - Stores selected role in localStorage
 * - Protected routes based on user role
 */
function App() {
  return (
    <Routes>
      {/* Default route - redirect to login */}
      <Route path="/" element={<Navigate to="/login" replace />} />
      
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
