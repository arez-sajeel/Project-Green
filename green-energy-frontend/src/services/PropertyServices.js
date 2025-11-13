const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

const headers = () => ({
  "Content-Type": "application/json",
  Authorization: `Bearer ${localStorage.getItem("access_token") || ""}`,
});

export async function createProperty(payload) {
  const res = await fetch(`${API_BASE}/properties`, {
    method: "POST", headers: headers(), body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
export async function updateProperty(id, payload) {
  const res = await fetch(`${API_BASE}/properties/${id}`, {
    method: "PUT", headers: headers(), body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
export async function getProperty(id) {
  const res = await fetch(`${API_BASE}/properties/${id}`, { headers: headers() });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}