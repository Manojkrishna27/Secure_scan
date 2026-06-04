import axios from "axios";

import { getApiMessage, unwrapApiData } from "@/utils/apiHelpers";

const TOKEN_KEY = "securescan_access_token";
const USER_KEY = "securescan_user";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:5000",
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 15000,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const url = error.config?.url || "";
      const isAuthRoute =
        url.includes("/api/auth/login") || url.includes("/api/auth/register");
      if (!isAuthRoute) {
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(USER_KEY);
        if (window.location.pathname !== "/login") {
          window.location.href = "/login";
        }
      }
    }
    return Promise.reject(error);
  }
);

export function getStoredToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function getStoredUser() {
  try {
    const raw = localStorage.getItem(USER_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function setAuthStorage(token, user) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function clearAuthStorage() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

export async function getHealth() {
  const response = await api.get("/api/health");
  return unwrapApiData(response);
}

export async function registerUser(payload) {
  const response = await api.post("/api/auth/register", payload);
  return unwrapApiData(response);
}

export async function loginUser(payload) {
  const response = await api.post("/api/auth/login", payload);
  return unwrapApiData(response);
}

export async function logoutUser() {
  const response = await api.post("/api/auth/logout");
  return unwrapApiData(response);
}

export async function fetchCurrentUser() {
  const response = await api.get("/api/auth/me");
  const data = unwrapApiData(response);
  return data.user;
}

export async function updateProfile(payload) {
  const response = await api.put("/api/auth/profile", payload);
  return unwrapApiData(response);
}

export async function changePassword(payload) {
  const response = await api.put("/api/auth/change-password", payload);
  return unwrapApiData(response);
}

export { TOKEN_KEY, USER_KEY, getApiMessage };
export default api;
