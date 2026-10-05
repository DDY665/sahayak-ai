// Validators Utility - Input Validation
import { FILE_CONFIG } from "../config/constants.js";
import { logger } from "./logger.js";

export class Validators {
  // Validate file for upload
  static validateFile(file) {
    if (!file) {
      return "No file selected";
    }

    if (file.size > FILE_CONFIG.MAX_SIZE_BYTES) {
      return `File size exceeds ${FILE_CONFIG.MAX_SIZE_MB}MB limit`;
    }

    const extension = file.name.split(".").pop().toLowerCase();
    if (!FILE_CONFIG.ALLOWED_EXTENSIONS.includes(extension)) {
      return `Invalid file type. Allowed: ${FILE_CONFIG.ALLOWED_EXTENSIONS.join(", ")}`;
    }

    if (!FILE_CONFIG.ALLOWED_TYPES.includes(file.type)) {
      logger.warn("MIME type mismatch", { fileName: file.name, mimeType: file.type });
    }

    return null;
  }

  // Validate question/message
  static validateQuestion(question) {
    if (!question || typeof question !== "string") {
      return "Question must be a non-empty string";
    }

    const trimmed = question.trim();
    if (trimmed.length === 0) {
      return "Question cannot be empty";
    }

    if (trimmed.length > 2000) {
      return "Question cannot exceed 2000 characters";
    }

    return null;
  }
}
