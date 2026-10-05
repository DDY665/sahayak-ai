import { useMemo } from "react";
import { marked } from "marked";
import DOMPurify from "dompurify";

marked.setOptions({
  gfm: true,
  breaks: true,
});

function MarkdownContent({ content }) {
  const html = useMemo(() => {
    if (!content) return "";
    try {
      return DOMPurify.sanitize(marked.parse(content));
    } catch {
      return content;
    }
  }, [content]);

  return (
    <div
      className="markdown-content"
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}

export default function ChatArea({ showEmpty, messages, uiText }) {
  const text = uiText || {
    emptyTitle: "Upload a document to begin",
    emptyDesc: "Your document will be analyzed and indexed for instant Q&A",
    suggestions: [
      "What's in this document?",
      "Summarize key points",
      "Find important dates",
    ],
    you: "You",
    ai: "AI",
    basedOn: "Based on",
    source: "source",
    sources: "sources",
  };
  const suggestions =
    Array.isArray(text.suggestions) && text.suggestions.length > 0
      ? text.suggestions
      : [
          "What's in this document?",
          "Summarize key points",
          "Find important dates",
        ];

  const visibleMessages = useMemo(() => {
    if (!Array.isArray(messages)) return [];
    const deduped = [];
    messages.forEach((msg) => {
      if (msg.hidden) return;
      const last = deduped[deduped.length - 1];
      if (
        last &&
        last.role === msg.role &&
        last.content.trim() === msg.content.trim()
      ) {
        return; // Deduplicate consecutive duplicate message
      }
      deduped.push(msg);
    });
    return deduped;
  }, [messages]);

  return (
    <>
      {showEmpty && (
        <div className="empty-state">
          <div className="empty-icon">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="1.8"
                d="M14 3H7a2 2 0 00-2 2v14a2 2 0 002 2h10a2 2 0 002-2V8z"
              />
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="1.8"
                d="M14 3v5h5"
              />
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="1.8"
                d="M9 13h6M9 17h4"
              />
            </svg>
          </div>
          <div className="empty-title">{text.emptyTitle}</div>
          <div className="empty-desc">{text.emptyDesc}</div>
          <div className="suggested-queries">
            {suggestions.map((item) => (
              <div key={item} className="suggestion-chip" aria-hidden="true">
                {item}
              </div>
            ))}
          </div>
        </div>
      )}

      <div className={`chat-messages ${showEmpty ? "chat-hidden" : ""}`}>
        {visibleMessages.map((msg, idx) => (
          <div className={`message ${msg.role}`} key={`${msg.role}-${idx}`}>
            <div className="avatar">
              {msg.role === "user" ? text.you : text.ai}
            </div>
            <div className="msg-body">
              <div className="bubble">
                {msg.role === "user" ? (
                  <div className="user-text">{msg.content}</div>
                ) : msg.content ? (
                  <MarkdownContent content={msg.content} />
                ) : (
                  <div className="typing-indicator">
                    <div className="typing-dot" />
                    <div className="typing-dot" />
                    <div className="typing-dot" />
                  </div>
                )}
              </div>
              {msg.role === "assistant" &&
              Array.isArray(msg.citations) &&
              msg.citations.length > 0 ? (
                <div className="source-line">
                  {text.basedOn} {msg.citations.length}{" "}
                  {msg.citations.length > 1 ? text.sources : text.source}
                </div>
              ) : null}
            </div>
          </div>
        ))}
      </div>
    </>
  );
}
