// src/services/authService.js

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

/**
 * Login user with email and password
 * @param {string} email - User's email
 * @param {string} password - User's password
 * @returns {Promise<{access_token: string, token_type: string}>}
 */
export async function loginUser(email, password) {
  // The backend expects OAuth2PasswordRequestForm format
  // which requires form data with 'username' and 'password' fields
  const formData = new URLSearchParams();
  formData.append('username', email); // Note: username field contains email
  formData.append('password', password);

  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData.toString(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Login failed');
  }

  const data = await response.json();
  return data; // Returns { access_token, token_type }
}

/**
 * Store authentication token in localStorage
 * @param {string} token - JWT access token
 */
export function saveToken(token) {
  localStorage.setItem('access_token', token);
}

/**
 * Get stored authentication token
 * @returns {string|null}
 */
export function getToken() {
  return localStorage.getItem('access_token');
}

/**
 * Remove authentication token (logout)
 */
export function clearToken() {
  localStorage.removeItem('access_token');
}

/**
 * Check if user is authenticated
 * @returns {boolean}
 */
export function isAuthenticated() {
  return !!getToken();
}
