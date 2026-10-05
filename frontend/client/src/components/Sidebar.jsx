import SidebarUploader from "./SidebarUploader.jsx";
import SidebarConversations from "./SidebarConversations.jsx";

export default function Sidebar({
  selectedFile,
  fileStatus,
  onUploadZoneClick,
  onUploadDocument,
  selectedLanguage,
  onLanguageChange,
  documentUploaded,
  chunksCount,
  uiText,
  loading,
  isOpen,
  user,
  onOpenAuth,
  onLogout,
  conversations = [],
  activeConversationId,
  onSelectConversation,
  onNewChat,
  onDeleteConversation,
}) {
  const text = uiText || {
    document: "Document",
    uploadDocument: "Upload Document",
    uploadSubtext: "PDF, TXT, DOC (max 15MB)",
    uploading: "Uploading...",
    language: "Language",
    documentInfo: "Document Info",
    sectionsIndexed: "Sections indexed",
  };

  return (
    <aside className={`left-panel ${isOpen ? "open" : ""}`}>
      {/* 1. ACCOUNT */}
      <div>
        <div className="panel-title">Account</div>
        {user ? (
          <div className="user-profile-badge">
            <div className="user-avatar">{user.name.charAt(0).toUpperCase()}</div>
            <div className="user-info">
              <span className="user-name">{user.name}</span>
              <span className="user-email">{user.email}</span>
            </div>
            <button className="logout-icon-btn" onClick={onLogout} title="Log Out" type="button">✕</button>
          </div>
        ) : (
          <button className="auth-btn" onClick={onOpenAuth} type="button">
            Log In / Sign Up
          </button>
        )}
      </div>

      {/* 2. CHAT THREADS */}
      {user && (
        <SidebarConversations
          conversations={conversations}
          activeConversationId={activeConversationId}
          onSelectConversation={onSelectConversation}
          onNewChat={onNewChat}
          onDeleteConversation={onDeleteConversation}
        />
      )}

      {/* 3. CONDITIONAL: BEFORE vs AFTER UPLOAD */}
      {!documentUploaded ? (
        <SidebarUploader
          selectedFile={selectedFile}
          fileStatus={fileStatus}
          onUploadZoneClick={onUploadZoneClick}
          onUploadDocument={onUploadDocument}
          selectedLanguage={selectedLanguage}
          onLanguageChange={onLanguageChange}
          chunksCount={chunksCount}
          loading={loading}
          text={text}
        />
      ) : (
        <div className="doc-info visible">
          <div className="panel-title">{text.documentInfo}</div>
          <div className="doc-stat">
            <span className="doc-stat-label">File Name</span>
            <span className="doc-stat-value" style={{ fontWeight: 600, wordBreak: "break-all" }}>
              {selectedFile?.name || fileStatus.name || "Uploaded Document"}
            </span>
          </div>
          <div className="doc-stat">
            <span className="doc-stat-label">{text.sectionsIndexed}</span>
            <span className="doc-stat-value">{chunksCount}</span>
          </div>
        </div>
      )}
    </aside>
  );
}
