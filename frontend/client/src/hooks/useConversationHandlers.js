// Conversation management handlers — select, new chat, delete
import { APIClient } from "../modules/api-client.js";

export function useConversationHandlers({
  user,
  activeConversationId,
  messages,
  setActiveConversationId,
  setSelectedLanguage,
  setDocumentUploaded,
  setChunksCount,
  setAnalysis,
  setFileStatus,
  setMessages,
  setLoading,
  setSelectedFile,
  setClarificationUI,
  setClarificationShownInSession,
  setConversations,
  refreshConversations,
  showToast,
}) {
  const handleSelectConversation = async (conversationId) => {
    if (activeConversationId === conversationId && messages.length > 0) return;
    setActiveConversationId(conversationId);
    setLoading(true);
    try {
      const data = await APIClient.getConversationMessages(conversationId);
      const conv = data.conversation || {};

      if (conv.language) setSelectedLanguage(conv.language);
      setDocumentUploaded(Boolean(conv.documentUploaded));
      setChunksCount(conv.chunksCount || "—");
      setAnalysis(conv.analysis || null);
      if (conv.documentName) {
        setFileStatus({ visible: true, name: conv.documentName, meta: `${conv.chunksCount || 0} sections indexed` });
      } else {
        setFileStatus({ visible: false, name: "", meta: "" });
      }

      if (Array.isArray(data.messages)) {
        const formatted = [];
        data.messages.forEach((msg) => {
          if (msg.question) formatted.push({ role: "user", content: msg.question });
          if (msg.answer) formatted.push({ role: "assistant", content: msg.answer, citations: msg.citations || [] });
        });
        setMessages(formatted);
      }
    } catch {
      showToast("Failed to load chat history", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleNewChat = () => {
    setActiveConversationId(null);
    setDocumentUploaded(false);
    setSelectedFile(null);
    setFileStatus({ visible: false, name: "", meta: "" });
    setChunksCount("—");
    setAnalysis(null);
    setMessages([]);
    setClarificationUI(null);
    setClarificationShownInSession(false);
  };

  const handleDeleteConversation = async (conversationId) => {
    try {
      await APIClient.deleteConversation(conversationId);
      if (activeConversationId === conversationId) handleNewChat();
      refreshConversations();
      showToast("Chat deleted");
    } catch {
      showToast("Failed to delete chat", "error");
    }
  };

  const handleAuthSuccess = (loggedUser) => {
    showToast(`Welcome back, ${loggedUser.name}!`);
  };

  const handleLogout = ({
    setUser,
    AUTH_TOKEN_KEY,
    AUTH_USER_KEY,
  }) => {
    localStorage.removeItem(AUTH_TOKEN_KEY);
    localStorage.removeItem(AUTH_USER_KEY);
    setUser(null);
    setConversations([]);
    setActiveConversationId(null);
    setDocumentUploaded(false);
    setMessages([]);
    showToast("Logged out successfully");
  };

  return {
    handleSelectConversation,
    handleNewChat,
    handleDeleteConversation,
    handleAuthSuccess,
    handleLogout,
  };
}
