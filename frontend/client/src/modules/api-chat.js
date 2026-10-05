// Chat/streaming API methods
import { API_BASE_URL, API_ENDPOINTS } from "../config/constants.js";
import { logger } from "../utils/logger.js";
import { getAuthHeaders } from "./api-auth.js";

export async function uploadDocument(file, options = {}) {
  try {
    logger.info("Uploading document", { filename: file.name, size: file.size });
    const formData = new FormData();
    formData.append("file", file);
    if (options.language) formData.append("language", options.language);
    if (options.conversationId) formData.append("conversationId", options.conversationId);

    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.UPLOAD}`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: formData
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || errorData.error || "Upload failed");
    }

    const data = await response.json();
    logger.info("Document uploaded successfully", { filename: file.name, chunks: data.chunks_created });
    return data;
  } catch (error) {
    logger.error("Document upload failed", error);
    throw error;
  }
}

export async function askQuestion(question, options = {}) {
  try {
    logger.info("Asking question", { question });
    const payload = {
      question,
      ...(options.language ? { language: options.language } : {}),
      ...(Array.isArray(options.history) ? { history: options.history } : {}),
      ...(options.conversationId ? { conversationId: options.conversationId } : {}),
      ...(options.documentName ? { documentName: options.documentName } : {}),
    };

    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.ASK}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...getAuthHeaders() },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || "Failed to get answer");
    }

    return await response.json();
  } catch (error) {
    logger.error("Failed to ask question", error);
    throw error;
  }
}

export async function* streamQuestion(question, options = {}) {
  try {
    logger.info("Starting stream question", { question });
    const payload = {
      question,
      ...(options.language ? { language: options.language } : {}),
      ...(Array.isArray(options.history) ? { history: options.history } : {}),
      ...(options.conversationId ? { conversationId: options.conversationId } : {}),
      ...(options.documentName ? { documentName: options.documentName } : {}),
    };

    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.ASK_STREAM}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...getAuthHeaders() },
      body: JSON.stringify(payload)
    });

    if (!response.ok) throw new Error(`Stream failed: ${response.status}`);

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true }).replace(/\r\n/g, "\n");
      const lines = buffer.split("\n\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        const trimmed = line.trim();
        if (trimmed.startsWith("data:")) {
          try {
            yield JSON.parse(trimmed.slice(5).trim());
          } catch (parseError) {
            logger.error("Failed to parse SSE event", parseError);
          }
        }
      }
    }

    const finalLine = buffer.trim();
    if (finalLine.startsWith("data:")) {
      try {
        yield JSON.parse(finalLine.slice(5).trim());
      } catch (parseError) {
        logger.error("Failed to parse final SSE event", parseError);
      }
    }
  } catch (error) {
    logger.error("Stream question failed", error);
    throw error;
  }
}
