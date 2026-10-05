// API Client — thin facade that re-exports all sub-modules as a unified APIClient class
// Sub-modules: api-auth.js (auth + conversations), api-chat.js (upload + ask + stream)
import {
  checkHealth,
  registerUser,
  loginUser,
  getConversations,
  createConversation,
  getConversationMessages,
  deleteConversation,
} from "./api-auth.js";

import {
  uploadDocument,
  askQuestion,
  streamQuestion,
} from "./api-chat.js";

export class APIClient {
  static checkHealth = checkHealth;
  static registerUser = registerUser;
  static loginUser = loginUser;
  static getConversations = getConversations;
  static createConversation = createConversation;
  static getConversationMessages = getConversationMessages;
  static deleteConversation = deleteConversation;
  static uploadDocument = uploadDocument;
  static askQuestion = askQuestion;
  static streamQuestion = streamQuestion;
}
