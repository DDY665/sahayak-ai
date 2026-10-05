import { APIClient } from "../modules/api-client.js";
import { Validators } from "../utils/validators.js";
import { parseClarificationPrompt } from "../utils/clarificationOptions.js";

export function useChatHandlers(state) {
  const {
    messageInput,
    setMessageInput,
    showToast,
    ui,
    documentUploaded,
    setClarificationUI,
    setLoading,
    messages,
    selectedLanguage,
    analysis,
    clarificationShownInSession,
    setMessages,
    setClarificationShownInSession,
    setAnalysisCollapsed,
    isListening,
    setIsListening,
    activeConversationId,
    setActiveConversationId,
    refreshConversations
  } = state;

  const onSend = async (questionOverride = "") => {
    if (state.loading) return;

    const question = String(questionOverride || messageInput).trim();
    if (!question) return;

    const validation = Validators.validateQuestion(question);
    if (validation) {
      showToast(validation, "error");
      return;
    }

    if (!documentUploaded) {
      showToast(ui.app.uploadDocumentFirst, "error");
      return;
    }
    setMessageInput("");
    setClarificationUI(null);
    if (setAnalysisCollapsed) setAnalysisCollapsed(true);
    setLoading(true);

    try {
      const history = messages.slice(-10).map((item) => ({ role: item.role, content: item.content }));
      let answer = "";
      let citations = [];
      let streamError = "";
      let returnedConvId = null;

      for await (const event of APIClient.streamQuestion(question, {
        language: selectedLanguage,
        history,
        conversationId: activeConversationId
      })) {
        if (event.type === "token" && event.token) {
          answer += event.token;
        }
        if (event.type === "citations_preview" && Array.isArray(event.citations)) {
          citations = event.citations;
        }
        if (event.type === "done" && event.conversationId) {
          returnedConvId = event.conversationId;
        }
        if (event.type === "error") {
          streamError = String(event.message || ui.app.streamFailed);
          break;
        }
      }

      if (!answer.trim()) {
        const fallback = await APIClient.askQuestion(question, {
          language: selectedLanguage,
          history,
          conversationId: activeConversationId
        });
        answer = String(fallback?.answer || streamError || ui.app.noResponse);
        citations = Array.isArray(fallback?.citations) ? fallback.citations : citations;
        if (fallback?.conversationId) returnedConvId = fallback.conversationId;
      }

      if (returnedConvId && returnedConvId !== activeConversationId && setActiveConversationId) {
        setActiveConversationId(returnedConvId);
        if (refreshConversations) refreshConversations();
      }

      const finalAnswer = answer || ui.app.noResponse;
      const clarification = parseClarificationPrompt(finalAnswer, analysis, selectedLanguage);

      if (clarification && !clarificationShownInSession) {
        setMessages((prev) => [...prev, { role: "assistant", content: finalAnswer, citations, hidden: true }]);
        setClarificationUI(clarification);
        setClarificationShownInSession(true);
        return;
      }

      setMessages((prev) => {
        const len = prev.length;
        if (
          len >= 2 &&
          prev[len - 2].content === question &&
          prev[len - 1].content === finalAnswer
        ) {
          return prev;
        }
        return [
          ...prev,
          { role: "user", content: question },
          { role: "assistant", content: finalAnswer, citations },
        ];
      });
    } catch (error) {
      showToast(String(error?.message || ui.app.cannotReachServer), "error");
    } finally {
      setLoading(false);
    }
  };

  const onVoiceToggle = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      showToast(ui.app.voiceUnsupported || "Speech recognition is not supported in this browser. Please use Chrome, Edge, or Safari.", "error");
      return;
    }

    if (isListening && recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch {}
      setIsListening(false);
      showToast("Voice recording stopped", "success");
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognitionRef.current = recognition;
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = selectedLanguage === "Hindi" ? "hi-IN" : selectedLanguage === "Telugu" ? "te-IN" : "en-US";

      recognition.onstart = () => {
        setIsListening(true);
        showToast("Listening... Speak now 🎙️", "success");
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognition.onerror = (event) => {
        setIsListening(false);
        if (event.error === "not-allowed") {
          showToast("Microphone access denied. Please click the mic icon in your browser address bar to allow permissions.", "error");
        } else if (event.error === "no-speech") {
          showToast("No speech detected. Please try speaking into your mic.", "error");
        } else if (event.error !== "aborted") {
          showToast(`Voice error: ${event.error}`, "error");
        }
      };

      recognition.onresult = (event) => {
        let text = "";
        for (let i = 0; i < event.results.length; i += 1) {
          text += event.results[i][0].transcript;
        }
        if (text.trim()) {
          setMessageInput(text.trim());
        }
      };

      recognition.start();
    } catch (err) {
      setIsListening(false);
      showToast(String(err?.message || "Failed to start microphone recognition"), "error");
    }
  };

  const onKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!state.loading) {
        onSend();
      }
    }
  };

  return { onSend, onVoiceToggle, onKeyDown };
}
