import { useState } from "react";
import Header from "./components/Header.jsx";
import Sidebar from "./components/Sidebar.jsx";
import AnalysisCard from "./components/AnalysisCard.jsx";
import ChatArea from "./components/ChatArea.jsx";
import Composer from "./components/Composer.jsx";
import AuthModal from "./components/AuthModal.jsx";
import { useAppController } from "./hooks/useAppController.js";

export default function App() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [panelHeight, setPanelHeight] = useState(115);

  const {
    theme,
    setTheme,
    health,
    selectedLanguage,
    setSelectedLanguage,
    selectedFile,
    fileStatus,
    documentUploaded,
    chunksCount,
    analysis,
    analysisCollapsed,
    setAnalysisCollapsed,
    messages,
    messageInput,
    setMessageInput,
    loading,
    isListening,
    clarificationUI,
    setClarificationUI,
    toast,
    ui,
    fileInputRef,
    showEmpty,
    user,
    authModalOpen,
    setAuthModalOpen,
    conversations,
    activeConversationId,
    handleAuthSuccess,
    handleLogout,
    handleSelectConversation,
    handleNewChat,
    handleDeleteConversation,
    onUploadZoneClick,
    onFileSelected,
    onUploadDocument,
    onSend,
    onVoiceToggle,
    onKeyDown,
  } = useAppController();

  return (
    <div className="app-shell">
      <Header
        theme={theme}
        onToggleTheme={() => setTheme((t) => (t === "dark" ? "light" : "dark"))}
        health={health}
        uiText={ui.header}
        mobileMenuOpen={mobileMenuOpen}
        onToggleMobileMenu={() => setMobileMenuOpen((open) => !open)}
      />

      <main>
        {mobileMenuOpen && (
          <div className="mobile-backdrop" onClick={() => setMobileMenuOpen(false)} role="presentation" />
        )}
        <Sidebar
          selectedFile={selectedFile}
          fileStatus={fileStatus}
          onUploadZoneClick={onUploadZoneClick}
          onUploadDocument={async (...args) => {
            await onUploadDocument(...args);
            setMobileMenuOpen(false);
          }}
          selectedLanguage={selectedLanguage}
          onLanguageChange={(lang) => {
            setSelectedLanguage(lang);
            setMobileMenuOpen(false);
          }}
          documentUploaded={documentUploaded}
          chunksCount={chunksCount}
          uiText={ui.sidebar}
          loading={loading}
          isOpen={mobileMenuOpen}
          user={user}
          onOpenAuth={() => setAuthModalOpen(true)}
          onLogout={handleLogout}
          conversations={conversations}
          activeConversationId={activeConversationId}
          onSelectConversation={(id) => {
            handleSelectConversation(id);
            setMobileMenuOpen(false);
          }}
          onNewChat={() => {
            handleNewChat();
            setMobileMenuOpen(false);
          }}
          onDeleteConversation={handleDeleteConversation}
        />

        <section className={`right-panel ${showEmpty ? "landing-mode" : ""}`}>
          {showEmpty ? (
            <div className="landing-container">
              <div className="empty-icon">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" d="M14 3H7a2 2 0 00-2 2v14a2 2 0 002 2h10a2 2 0 002-2V8z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" d="M14 3v5h5" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" d="M9 13h6M9 17h4" />
                </svg>
              </div>
              <h1 className="empty-title">{ui.chat?.emptyTitle || "Upload a document to begin"}</h1>
              <p className="empty-desc">{ui.chat?.emptyDesc || "Your document will be analyzed and indexed for instant Q&A"}</p>

              <Composer
                message={messageInput}
                onMessageChange={setMessageInput}
                onSend={onSend}
                onKeyDown={onKeyDown}
                onVoiceToggle={onVoiceToggle}
                listening={isListening}
                disabled={loading}
                clarification={clarificationUI}
                uiText={ui.composer}
                onClarificationSelect={(option) => {
                  onSend(option?.prompt || option?.label || "");
                }}
                onClarificationSkip={() => setClarificationUI(null)}
              />

              <div className="suggested-queries">
                {(ui.chat?.suggestions || ["What's in this document?", "Summarize key points", "Find important dates"]).map((item) => (
                  <button
                    key={item}
                    type="button"
                    className="suggestion-chip"
                    onClick={() => onSend(item)}
                  >
                    {item}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <>
              <AnalysisCard
                analysis={analysis}
                language={selectedLanguage}
                onHeightChange={(h) => setPanelHeight(h)}
              />

              {analysis && panelHeight > 130 && (
                <div className="chat-backdrop-overlay" />
              )}

              <div
                className={`chat-messages-container ${analysis && panelHeight > 130 ? "chat-blurred-disabled" : ""}`}
                style={{ marginTop: analysis ? "115px" : "0px" }}
              >
                <ChatArea
                  showEmpty={showEmpty}
                  messages={messages}
                  uiText={ui.chat}
                />
              </div>

              <Composer
                message={messageInput}
                onMessageChange={setMessageInput}
                onSend={onSend}
                onKeyDown={onKeyDown}
                onVoiceToggle={onVoiceToggle}
                listening={isListening}
                disabled={loading || (analysis && panelHeight > 130)}
                clarification={clarificationUI}
                uiText={ui.composer}
                onClarificationSelect={(opt) => {
                  onSend(`${opt.id}. ${opt.label}`);
                  setClarificationUI(null);
                }}
                onClarificationSkip={() => setClarificationUI(null)}
              />
            </>
          )}
        </section>
      </main>

      <input
        ref={fileInputRef}
        type="file"
        className="file-input-hidden"
        accept=".pdf,.txt,.doc,.docx"
        aria-label={ui.fileInputLabel}
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) onFileSelected(file);
        }}
      />

      <AuthModal
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        onAuthSuccess={handleAuthSuccess}
      />

      <div className={`toast ${toast.type} ${toast.show ? "show" : ""}`}>{toast.text}</div>
    </div>
  );
}
