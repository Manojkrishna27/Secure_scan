/** Extract user-facing message from API errors (standard + legacy shape). */
export function getApiMessage(error, fallback = "Something went wrong. Please try again.") {
  return (
    error?.response?.data?.message ||
    error?.response?.data?.error ||
    error?.message ||
    fallback
  );
}

/** Unwrap standardized { success, message, data } responses. */
export function unwrapApiData(response) {
  const body = response.data;
  if (body && typeof body.success === "boolean") {
    if (!body.success) {
      const err = new Error(body.message || "Request failed");
      err.response = response;
      throw err;
    }
    return body.data ?? {};
  }
  return body ?? {};
}
