import api from "./api";
import { unwrapApiData } from "@/utils/apiHelpers";

export async function addDomain(domain, monitoringFrequency = "daily") {
  const response = await api.post("/api/monitoring", {
    domain,
    monitoring_frequency: monitoringFrequency,
  });
  return unwrapApiData(response);
}

export async function getDomains() {
  const response = await api.get("/api/monitoring");
  const data = unwrapApiData(response);
  return data.domains ?? [];
}

export async function getMonitoringSummary() {
  const response = await api.get("/api/monitoring/summary");
  return unwrapApiData(response);
}

export async function getMonitoringTrends(limit = 30) {
  const response = await api.get("/api/monitoring/trends", { params: { limit } });
  const data = unwrapApiData(response);
  return data.trends ?? [];
}

export async function updateDomain(id, payload) {
  const response = await api.put(`/api/monitoring/${id}`, payload);
  return unwrapApiData(response);
}

export async function deleteDomain(id) {
  const response = await api.delete(`/api/monitoring/${id}`);
  return unwrapApiData(response);
}

export async function runScan(id) {
  const response = await api.post(`/api/monitoring/${id}/scan`, null, {
    timeout: 120000,
  });
  return unwrapApiData(response);
}
