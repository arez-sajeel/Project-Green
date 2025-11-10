import { Navigate } from "react-router-dom";
import { isAuthenticated } from "../services/authService";

/**
 * RoleProtectedRoute - Sprint 1.5: Role-Based Access Control
 * 
 * Protects routes based on user role and authentication status.
 * Redirects to login if not authenticated, or to appropriate dashboard if wrong role.
 */
export default function RoleProtectedRoute({ allowedRole, children }) {
  // Check if user is authenticated
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }

  // Get the user's role from localStorage
  const userRole = localStorage.getItem("userRole");

  if (!userRole) {
    // No role set - redirect to role selection
    return <Navigate to="/role" replace />;
  }

  // Check if user has the required role
  if (userRole !== allowedRole) {
    // Redirect to the correct dashboard based on their actual role
    if (userRole === "Homeowner") {
      return <Navigate to="/homeowner-dashboard" replace />;
    } else if (userRole === "PropertyManager") {
      return <Navigate to="/manager-dashboard" replace />;
    }
    // Fallback to login
    return <Navigate to="/login" replace />;
  }

  // User has correct role - render the protected content
  return children;
}
