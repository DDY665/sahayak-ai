import { useEffect, useMemo, useRef, useState } from "react";

import { APIClient } from "../modules/api-client.js";
import { getUIStrings } from "../i18n/strings.js";
import { useAppHandlers } from "./useAppHandlers.js";
import { useConversationHandlers } from "./useConversationHandlers.js";
import { AUTH_TOKEN_KEY, AUTH_USER_KEY } from "../config/constants.js";

function initialTheme() {
  return localStorage.getItem("selectedTheme") || "dark";
}

function initialLanguage() {
  return localStorage.getItem("selectedLanguage") || "English";
}

function initialUser() {
  try {
    const raw = localStorage.getItem(AUTH_USER_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function useAppController() {
  const [theme, setTheme] = useState(initialTheme);
  const [health, setHealth] = useState({ node: "offline", python: "offline" });
  const [selectedLanguage, setSelectedLanguage] = useState(initialLanguage);
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileStatus, setFileStatus] = useState({ visible: false, name: "", meta: "" });
  const [documentUploaded, setDocumentUploaded] = useState(false);
  const [chunksCount, setChunksCount] = useState("—");
  const [analysis, setAnalysis] = useState(null);
  const [analysisCollapsed, setAnalysisCollapsed] = useState(false);
  const [messages, setMessages] = useState([]);
  const [messageInput, setMessageInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [clarificationUI, setClarificationUI] = useState(null);
  const [clarificationShownInSession, setClarificationShownInSession] = useState(false);
  const [toast, setToast] = useState({ show: false, text: "", type: "success" });
  const [user, setUser] = useState(initialUser);
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);

  const ui = useMemo(() => getUIStrings(selectedLanguage), [selectedLanguage]);
  const fileInputRef = useRef(null);
  const recognitionRef = useRef(null);

  useEffect(() => {
    document.body.classList.toggle("dark", theme === "dark");
    localStorage.setItem("selectedTheme", theme);
  }, [theme]);

  useEffect(() => {
    localStorage.setItem("selectedLanguage", selectedLanguage);
  }, [selectedLanguage]);

  useEffect(() => {
    const runHealth = async () => {
      try {
        const data = await APIClient.checkHealth();
        setHealth(data);
      } catch {
        setHealth({ node: "offline", python: "offline" });
      }
    };
    runHealth();
    const timer = setInterval(runHealth, 5000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    if (!toast.show) return undefined;
    const t = setTimeout(() => setToast((prev) => ({ ...prev, show: false })), 3000);
    return () => clearTimeout(t);
  }, [toast.show]);

  const showToast = (text, type = "success") => setToast({ show: true, text, type });

  const refreshConversations = async () => {
    if (!user) { setConversations([]); return; }
    const data = await APIClient.getConversations();
    setConversations(data.conversations || []);
  };

  useEffect(() => { refreshConversations(); }, [user]); // eslint-disable-line react-hooks/exhaustive-deps

  const sharedState = {
    user, activeConversationId, messages,
    setActiveConversationId, setSelectedLanguage, setDocumentUploaded,
    setChunksCount, setAnalysis, setFileStatus, setMessages,
    setLoading, setSelectedFile, setClarificationUI, setClarificationShownInSession,
    setConversations, refreshConversations, showToast,
  };

  const {
    handleSelectConversation,
    handleNewChat,
    handleDeleteConversation,
    handleAuthSuccess: _handleAuthSuccess,
    handleLogout: _handleLogout,
  } = useConversationHandlers(sharedState);

  const handleAuthSuccess = (loggedUser) => {
    setUser(loggedUser);
    _handleAuthSuccess(loggedUser);
  };

  const handleLogout = () => {
    _handleLogout({ setUser, AUTH_TOKEN_KEY, AUTH_USER_KEY });
  };

  const handlers = useAppHandlers({
    selectedFile, setSelectedFile, setFileStatus, selectedLanguage,
    setDocumentUploaded, setChunksCount, setAnalysis, setAnalysisCollapsed,
    setClarificationShownInSession, setMessages, setLoading, fileInputRef,
    showToast, ui, messageInput, setMessageInput, setClarificationUI,
    documentUploaded, messages, analysis, clarificationShownInSession,
    isListening, setIsListening, recognitionRef,
    activeConversationId, setActiveConversationId, refreshConversations,
  });

  const showEmpty = !documentUploaded && messages.length === 0 && !loading;

  return {
    theme, setTheme, health, selectedLanguage, setSelectedLanguage,
    selectedFile, fileStatus, documentUploaded, chunksCount, analysis,
    analysisCollapsed, setAnalysisCollapsed, messages, messageInput,
    setMessageInput, loading, isListening, clarificationUI, setClarificationUI,
    toast, ui, fileInputRef, showEmpty, user, authModalOpen, setAuthModalOpen,
    conversations, activeConversationId,
    handleAuthSuccess, handleLogout, handleSelectConversation,
    handleNewChat, handleDeleteConversation,
    ...handlers,
  };
}
