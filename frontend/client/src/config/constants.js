// API Configuration
export const API_BASE_URL = "http://localhost:8000";
export const API_ENDPOINTS = {
  HEALTH: "/health",
  UPLOAD: "/api/upload",
  DOCUMENTS: "/api/documents",
  ASK: "/api/ask",
  ASK_STREAM: "/api/ask/stream",
  AUTH_REGISTER: "/api/auth/register",
  AUTH_LOGIN: "/api/auth/login",
  AUTH_ME: "/api/auth/me",
  CONVERSATIONS: "/api/conversations"
};

export const AUTH_TOKEN_KEY = "sahayakai_auth_token";
export const AUTH_USER_KEY = "sahayakai_auth_user";

// File Upload Configuration
export const FILE_CONFIG = {
  MAX_SIZE_MB: 15,
  MAX_SIZE_BYTES: 15 * 1024 * 1024,
  ALLOWED_EXTENSIONS: ["pdf", "txt", "docx"],
  ALLOWED_TYPES: [
    "application/pdf",
    "text/plain",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
  ]
};
