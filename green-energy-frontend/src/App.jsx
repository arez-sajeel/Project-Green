import { Routes, Route } from "react-router-dom";
import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";
import HomeOwner from "./pages/HomeOwner.jsx";
import SelectRole from "./pages/SelectRole.jsx";
import PropertyManagerDashboard from "./pages/PropertyManagerDashboard";
import PropertyManagerSetup from "./pages/PropertyManagerSetup";
import HomeownerSetup from "./pages/HomeownerSetup";
import HomeownerDashboard from "./pages/HomeownerDashboard";

function App() {
  return (
    <Routes>
<Route path="/role" element={<SelectRole />} />
<Route path="/login" element={<Login />} />
<Route path="/register" element={<Register />} />
<Route path="/homeowner" element={<HomeOwner />} />
<Route path="/manager" element={<Manager />} />
<Route path="/homeowner-setup" element={<HomeownerSetup />} />
<Route path="/property-manager-setup" element={<PropertyManagerSetup />} />
<Route path="/homeowner-dashboard" element={<HomeownerDashboard />} />
<Route path="/manager-dashboard" element={<PropertyManagerDashboard />} />

    </Routes>
  );
}

export default App;
