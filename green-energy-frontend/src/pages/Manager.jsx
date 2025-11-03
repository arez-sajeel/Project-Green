import { logout, getSession } from "../services-temp/mockAuth";
import { useNavigate } from "react-router-dom";

export default function Manager() {
  const nav = useNavigate();
  const session = getSession();

  return (
    <div style={{ padding: 24, fontFamily: "system-ui" }}>
      <h2>Property Manager Dashboard</h2>
      <p>Signed in as <b>{session?.email}</b></p>
      <button onClick={() => { logout(); nav("/login"); }}>Log out</button>
      <div style={{ marginTop: 16, opacity: 0.8 }}>
        <em>Placeholder: portfolio view, tariff config, API-backed widgets…</em>
      </div>
    </div>
  );
}
