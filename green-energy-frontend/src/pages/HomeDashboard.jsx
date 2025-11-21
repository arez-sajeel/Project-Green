import { logout, getSession } from "../services-temp/mockAuth";
import { useNavigate } from "react-router-dom";

export default function HomeownerDashboard() {
  const nav = useNavigate();

  return (
    <div style={{ padding: 24, fontFamily: "system-ui" }}>
      <h2>Home Dashboard</h2>
      <p>Quick links to your home systems</p>

      <div style={{ display: "grid", gap: 12, maxWidth: 360, marginTop: 20 }}>
        <button onClick={() => nav("/energy-usage")}>
          Energy Usage
        </button>

        <button onClick={() => nav("/devices")}>
          Devices
        </button>

        <button onClick={() => nav("/reports")}>
          Reports
        </button>

        <button onClick={() => nav("/account")}>
          Account
        </button>
      </div>

      <div style={{ marginTop: 24, opacity: 0.75 }}>
        <em>Placeholder: dashboard widgets, charts, tiles…</em>
      </div>
    </div>
  );
}

