import api from "./api";
import { unwrapApiData } from "@/utils/apiHelpers";

export async function generateReport(scanId) {
  const response = await api.post(`/api/reports/generate/${scanId}`, null, {
    timeout: 60000,
  });
  const data = unwrapApiData(response);
  return { report: data.report, message: response.data?.message };
}

export async function getReports() {
  const response = await api.get("/api/reports");
  const data = unwrapApiData(response);
  return data.reports ?? [];
}

export async function getReportById(reportId) {
  const response = await api.get(`/api/reports/${reportId}`);
  const data = unwrapApiData(response);
  return data.report;
}

export async function downloadReport(reportId) {
  return api.get(`/api/reports/download/${reportId}`, {
    responseType: "blob",
  });
}

export async function deleteReport(reportId) {
  const response = await api.delete(`/api/reports/${reportId}`);
  return unwrapApiData(response);
}

/**
 * Save the PDF blob as a file download.
 * Uses the blob directly — do NOT wrap in new Blob([blob]) or it corrupts.
 */
export function savePdfBlob(blob, filename) {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}

/**
 * Open the PDF blob in a new browser tab for inline viewing.
 */
export function openPdfBlob(blob) {
  const url = window.URL.createObjectURL(blob);
  window.open(url, "_blank", "noopener,noreferrer");
  // Revoke after a short delay so the tab has time to read it
  setTimeout(() => window.URL.revokeObjectURL(url), 10000);
}
