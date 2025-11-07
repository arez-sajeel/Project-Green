// Temporary mock auth service
// This provides basic auth functions for the dashboard pages

export function getSession() {
  const token = localStorage.getItem('accessToken');
  const userInfo = localStorage.getItem('userInfo');
  
  if (!token || !userInfo) {
    return null;
  }
  
  try {
    return JSON.parse(userInfo);
  } catch (e) {
    return null;
  }
}

export function logout() {
  localStorage.removeItem('accessToken');
  localStorage.removeItem('userInfo');
}

export function isAuthenticated() {
  return !!localStorage.getItem('accessToken');
}
