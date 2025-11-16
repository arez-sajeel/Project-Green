import { getToken } from "./authService";

const API_URL = "http://localhost:8000"; // ← change if needed

export async function fetchUserContext() {
  const token = getToken();

  const res = await fetch(`${API_URL}/context`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!res.ok) throw new Error("Failed to load properties");
  return res.json();
}

export async function addProperty(propertyId, providerCode) {
  const token = getToken();

  const body = {
    property_id: propertyId,
    provider_code: providerCode,
  };

  const res = await fetch(`${API_URL}/properties`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  if (!res.ok) throw new Error("Failed to add property");
  return res.json();
}
