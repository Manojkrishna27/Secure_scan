import api from "./api";
import { unwrapApiData } from "@/utils/apiHelpers";

export async function getNotifications(limit = 50) {
  const response = await api.get("/api/notifications", { params: { limit } });
  const data = unwrapApiData(response);
  return data.notifications ?? [];
}

export async function getUnreadCount() {
  const response = await api.get("/api/notifications/unread-count");
  const data = unwrapApiData(response);
  return data.unread_count ?? 0;
}

export async function markAsRead(id) {
  const response = await api.put(`/api/notifications/${id}/read`);
  return unwrapApiData(response);
}

export async function deleteNotification(id) {
  const response = await api.delete(`/api/notifications/${id}`);
  return unwrapApiData(response);
}
