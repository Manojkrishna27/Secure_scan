import api from "./api";
import { unwrapApiData } from "@/utils/apiHelpers";

export async function startScan(url) {
  const response = await api.post("/api/scans", { url }, { timeout: 120000 });
  const data = unwrapApiData(response);
  return { scan: data.scan, message: response.data?.message };
}

export async function getScans(params = {}) {
  const response = await api.get("/api/scans", { params });
  const data = unwrapApiData(response);
  return data.scans ?? [];
}

export async function getScanById(id) {
  const response = await api.get(`/api/scans/${id}`);
  const data = unwrapApiData(response);
  return data.scan;
}

export async function deleteScan(id) {
  const response = await api.delete(`/api/scans/${id}`);
  return unwrapApiData(response);
}
