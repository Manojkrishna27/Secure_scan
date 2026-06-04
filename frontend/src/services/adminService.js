import api from "./api";
import { unwrapApiData } from "@/utils/apiHelpers";

export async function getAdminStats() {
  const response = await api.get("/api/admin/stats");
  return unwrapApiData(response);
}

export async function getAdminAnalytics(period = "daily") {
  const response = await api.get("/api/admin/analytics", { params: { period } });
  return unwrapApiData(response);
}

export async function getAdminRecent() {
  const response = await api.get("/api/admin/recent");
  return unwrapApiData(response);
}

export async function getAdminHealth() {
  const response = await api.get("/api/admin/health");
  return unwrapApiData(response);
}

export async function getAdminUsers(includeDeleted = false) {
  const response = await api.get("/api/admin/users", {
    params: { include_deleted: includeDeleted },
  });
  const data = unwrapApiData(response);
  return data.users ?? [];
}

export async function getAdminUser(id) {
  const response = await api.get(`/api/admin/users/${id}`);
  const data = unwrapApiData(response);
  return data.user;
}

export async function updateAdminUser(id, payload) {
  const response = await api.put(`/api/admin/users/${id}`, payload);
  return unwrapApiData(response);
}

export async function deleteAdminUser(id) {
  const response = await api.delete(`/api/admin/users/${id}`);
  return unwrapApiData(response);
}

export async function getAuditLogs(params = {}) {
  const response = await api.get("/api/admin/audit-logs", { params });
  return unwrapApiData(response);
}

export async function adminSearch(q, limit = 10) {
  const response = await api.get("/api/admin/search", { params: { q, limit } });
  return unwrapApiData(response);
}

function downloadCsv(path, filename) {
  return api.get(path, { responseType: "blob" }).then((res) => {
    const url = window.URL.createObjectURL(new Blob([res.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  });
}

export const exportUsersCsv = () => downloadCsv("/api/admin/export/users", "users.csv");
export const exportScansCsv = () => downloadCsv("/api/admin/export/scans", "scans.csv");
export const exportAuditLogsCsv = () =>
  downloadCsv("/api/admin/export/audit-logs", "audit_logs.csv");
