import { Navigate } from "react-router-dom";

export default function RoleProtectedRoute({ allowedRole, children }) {
  const role = localStorage.getItem("role"); // stored at login

  if (!role) {
    return <Navigate to="/login" replace />;
  }

  if (role !== allowedRole) {
    return <Navigate to="/login" replace />;
  }

  return children;
}
