// Auth API methods
import { API_BASE_URL, API_ENDPOINTS, AUTH_TOKEN_KEY } from "../config/constants.js";
import { logger } from "../utils/logger.js";

export function getAuthHeaders(token = null) {
  const activeToken = token || localStorage.getItem(AUTH_TOKEN_KEY);
  return activeToken ? { Authorization: `Bearer ${activeToken}` } : {};
}

export async function checkHealth() {
  try {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.HEALTH}`);
    if (!response.ok) throw new Error(`Health check failed: ${response.status}`);
    return await response.json();
  } catch (error) {
    logger.error("Health check failed", error);
    throw error;
  }
}

export async function registerUser(name, email, password) {
  try {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.AUTH_REGISTER}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email, password })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Registration failed");
    return data;
  } catch (error) {
    logger.error("Registration failed", error);
    throw error;
  }
}

export async function loginUser(email, password) {
  try {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.AUTH_LOGIN}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Login failed");
    return data;
  } catch (error) {
    logger.error("Login failed", error);
    throw error;
  }
}

export async function getConversations() {
  try {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.CONVERSATIONS}`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error("Failed to fetch conversations");
    return await response.json();
  } catch (error) {
    logger.error("Failed to fetch conversations", error);
    return { conversations: [] };
  }
}

export async function createConversation(title, documentName = null) {
  try {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.CONVERSATIONS}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...getAuthHeaders() },
      body: JSON.stringify({ title, documentName })
    });
    if (!response.ok) throw new Error("Failed to create conversation");
    return await response.json();
  } catch (error) {
    logger.error("Failed to create conversation", error);
    throw error;
  }
}

export async function getConversationMessages(conversationId) {
  try {
    const response = await fetch(
      `${API_BASE_URL}${API_ENDPOINTS.CONVERSATIONS}/${conversationId}/messages`,
      { headers: getAuthHeaders() }
    );
    if (!response.ok) throw new Error("Failed to fetch messages");
    return await response.json();
  } catch (error) {
    logger.error("Failed to fetch conversation messages", error);
    throw error;
  }
}

export async function deleteConversation(conversationId) {
  try {
    const response = await fetch(
      `${API_BASE_URL}${API_ENDPOINTS.CONVERSATIONS}/${conversationId}`,
      { method: "DELETE", headers: getAuthHeaders() }
    );
    if (!response.ok) throw new Error("Failed to delete conversation");
    return await response.json();
  } catch (error) {
    logger.error("Failed to delete conversation", error);
    throw error;
  }
}
