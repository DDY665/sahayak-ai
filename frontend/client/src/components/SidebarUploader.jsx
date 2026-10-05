// Language selector + Upload zone — shown only before a file is uploaded
const LANGUAGES = [
  { value: "English", label: "English", flag: "🇬🇧", code: "GB" },
  { value: "Hindi", label: "हिंदी", flag: "🇮🇳", code: "IN" },
  { value: "Telugu", label: "తెలుగు", flag: "🇮🇳", code: "IN" }
];

export default function SidebarUploader({
  selectedFile,
  fileStatus,
  onUploadZoneClick,
  onUploadDocument,
  selectedLanguage,
  onLanguageChange,
  chunksCount,
  loading,
  text,
}) {
  return (
    <>
      {/* LANGUAGE SELECTION */}
      <div className="language-section">
        <div className="panel-title">{text.language}</div>
        <div className="lang-instruction">Select a language</div>
        <div className="lang-options">
          {LANGUAGES.map((lang) => (
            <label className={`lang-option ${selectedLanguage === lang.value ? "selected" : ""}`} key={lang.value}>
              <input
                type="radio"
                name="language"
                value={lang.value}
                checked={selectedLanguage === lang.value}
                onChange={() => onLanguageChange(lang.value)}
              />
              <span className="lang-flag">{lang.code}</span>
              <span>{lang.label}</span>
            </label>
          ))}
        </div>
      </div>

      {/* UPLOAD DROPZONE */}
      <div>
        <div className="panel-title">{text.document}</div>
        <div className="upload-zone" onClick={onUploadZoneClick} role="button" tabIndex={0}>
          <div className="upload-icon">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
          </div>
          <div className="upload-text">{text.uploadDocument}</div>
          <div className="upload-subtext">{text.uploadSubtext}</div>
        </div>

        <div className={`file-status ${fileStatus.visible ? "visible" : ""}`}>
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <div className="file-name">{selectedFile?.name || fileStatus.name || ""}</div>
            <div className="file-meta">{fileStatus.meta || ""}</div>
          </div>
        </div>

        <button className={`upload-btn ${selectedFile ? "visible" : ""}`} onClick={onUploadDocument} type="button" disabled={loading}>
          {loading ? text.uploading : text.uploadDocument}
        </button>
      </div>
    </>
  );
}
