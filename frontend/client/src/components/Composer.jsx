import { useEffect, useState } from "react";

export default function Composer({
  message,
  onMessageChange,
  onSend,
  onKeyDown,
  onVoiceToggle,
  listening,
  disabled,
  clarification,
  uiText,
  onClarificationSelect,
  onClarificationSkip
}) {
  const text = uiText || {
    pickerHelp: "↑↓ to navigate · Enter to select · Esc to skip",
    skip: "Skip",
    skipClarification: "Skip clarification",
    askPlaceholder: "Ask a question, or tap to speak.",
    voiceInput: "Voice input",
    sendMessage: "Send message",
    inputHint: "Press Enter to send · Shift+Enter for new line"
  };
  const [activeIndex, setActiveIndex] = useState(0);

  useEffect(() => {
    if (!clarification) return;
    setActiveIndex(0);
  }, [clarification]);

  useEffect(() => {
    if (!clarification) return undefined;

    const onPickerKeyDown = (event) => {
      const targetTag = event.target?.tagName;
      const inTextInput = targetTag === "INPUT" || targetTag === "TEXTAREA";

      if (event.key === "Escape") {
        event.preventDefault();
        onClarificationSkip?.();
        return;
      }

      if (inTextInput) return;

      if (event.key === "ArrowDown") {
        event.preventDefault();
        setActiveIndex((idx) => (idx + 1) % clarification.options.length);
      }

      if (event.key === "ArrowUp") {
        event.preventDefault();
        setActiveIndex((idx) => (idx - 1 + clarification.options.length) % clarification.options.length);
      }

      if (event.key === "Enter") {
        event.preventDefault();
        const selected = clarification.options[activeIndex];
        if (selected) onClarificationSelect?.(selected);
      }
    };

    window.addEventListener("keydown", onPickerKeyDown);
    return () => window.removeEventListener("keydown", onPickerKeyDown);
  }, [clarification, activeIndex, onClarificationSelect, onClarificationSkip]);

  return (
    <div className="input-area">
      {clarification ? (
        <div className="clarification-picker" role="group" aria-label="Clarification picker">
          <div className="clarification-head">
            <div className="clarification-title">{clarification.prompt}</div>
            <button
              type="button"
              className="clarification-close"
              onClick={onClarificationSkip}
              aria-label={text.skipClarification}
              disabled={disabled}
            >
              ×
            </button>
          </div>

          <div className="clarification-options">
            {clarification.options.map((option, index) => (
              <button
                key={option.id}
                type="button"
                className={`clarification-option ${index === activeIndex ? "active" : ""}`}
                onClick={() => onClarificationSelect?.(option)}
                disabled={disabled}
              >
                <span className="clarification-option-number">{option.id}</span>
                <span className="clarification-option-text">{option.label}</span>
              </button>
            ))}
          </div>

          <div className="input-wrapper clarification-input-wrapper">
            <textarea
              id="questionInput"
              placeholder={text.askPlaceholder}
              rows="1"
              value={message}
              onChange={(e) => onMessageChange(e.target.value)}
              onKeyDown={onKeyDown}
              disabled={disabled}
            />
            <button className={`mic-btn ${listening ? "listening" : ""}`} id="micBtn" title={text.voiceInput} type="button" onClick={onVoiceToggle}>
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" d="M12 3a3 3 0 00-3 3v6a3 3 0 006 0V6a3 3 0 00-3-3z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" d="M19 11a7 7 0 01-14 0m7 7v3m-3 0h6" />
              </svg>
            </button>
            <button className="send-btn" id="sendBtn" disabled={disabled || !message.trim()} aria-label={text.sendMessage} title={text.sendMessage} type="button" onClick={onSend}>
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
            </button>
          </div>

          <div className="clarification-footer">
            <span>{text.pickerHelp}</span>
            <button type="button" className="clarification-skip" onClick={onClarificationSkip} disabled={disabled}>
              {text.skip}
            </button>
          </div>
        </div>
      ) : null}

      {!clarification ? (
        <>
          <div className="input-wrapper">
            <textarea
              id="questionInput"
              placeholder={text.askPlaceholder}
              rows="1"
              value={message}
              onChange={(e) => onMessageChange(e.target.value)}
              onKeyDown={onKeyDown}
              disabled={disabled}
            />
            <button className={`mic-btn ${listening ? "listening" : ""}`} id="micBtn" title={text.voiceInput} type="button" onClick={onVoiceToggle}>
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" d="M12 3a3 3 0 00-3 3v6a3 3 0 006 0V6a3 3 0 00-3-3z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" d="M19 11a7 7 0 01-14 0m7 7v3m-3 0h6" />
              </svg>
            </button>
            <button className="send-btn" id="sendBtn" disabled={disabled || !message.trim()} aria-label={text.sendMessage} title={text.sendMessage} type="button" onClick={onSend}>
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
            </button>
          </div>
          <div className={`input-hint ${listening ? "listening-hint" : ""}`}>
            {listening ? "🎙️ Listening... Speak into your mic (click mic again to stop)" : text.inputHint}
          </div>
        </>
      ) : null}
    </div>
  );
}
