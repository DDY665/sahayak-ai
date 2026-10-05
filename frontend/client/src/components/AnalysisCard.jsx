import { esc, looksNoisySummary, buildReadableSummary } from "./analysis/cardHelpers.js";
import { getCardText } from "./analysis/cardLocales.js";
import HighlightsPanel from "./analysis/HighlightsPanel.jsx";
import { useAnalysisDrag } from "../hooks/useAnalysisDrag.js";

export default function AnalysisCard({ analysis, language = "English", onHeightChange }) {
  const { height, handleStartDrag } = useAnalysisDrag(onHeightChange);

  if (!analysis) return null;

  const text = getCardText(language);
  const docType = analysis.doc_type || "unknown";
  const typeToneMap = {
    medical: "sc-tone-medical",
    bank: "sc-tone-finance",
    government: "sc-tone-government",
    unknown: "sc-tone-generic",
  };

  const highlights = Array.isArray(analysis.highlights) ? analysis.highlights : [];
  const importantDates = Array.isArray(analysis.important_dates) ? analysis.important_dates : [];
  const importantPoints = Array.isArray(analysis.important_points)
    ? analysis.important_points
    : Array.isArray(analysis.important_details) ? analysis.important_details : [];
  const medicalConclusion = String(analysis.medical_conclusion || "").trim();
  const rawSummary = String(analysis.summary || "").trim();
  const displaySummary = looksNoisySummary(rawSummary)
    ? buildReadableSummary(analysis, language)
    : rawSummary;

  const importantPointKeys = new Set(
    importantPoints
      .map((item) => `${String(item?.label || "").toLowerCase()}|${String(item?.value || "").toLowerCase()}`)
      .filter((key) => key !== "|")
  );

  const filteredHighlights = highlights.filter((item) => {
    const key = `${String(item?.name || "").toLowerCase()}|${String(item?.value || "").toLowerCase()}`;
    if (importantPointKeys.has(key)) return false;
    const value = String(item?.value || "").toLowerCase();
    return !Array.from(importantPointKeys).some((k) => {
      const pv = k.split("|")[1] || "";
      return pv && value && (pv.includes(value) || value.includes(pv));
    });
  });

  const combinedImportantRows = (() => {
    const rows = [];
    const seen = new Set();
    const pushRow = (name, value, note, status = "important", reference_range = "") => {
      const n = String(name || text.item).trim();
      const v = String(value || "").trim();
      const key = `${n.toLowerCase()}|${v.toLowerCase()}`;
      if (!n || !v || seen.has(key)) return;
      seen.add(key);
      rows.push({ name: n, value: v, note: String(note || "").trim(), status, reference_range });
    };
    importantDates.forEach((item) => pushRow(item.label || text.date, item.value, item.note, "deadline"));
    importantPoints.forEach((item) => pushRow(item.label || text.detail, item.value, item.note, "important"));
    filteredHighlights.forEach((item) => pushRow(item.name || text.item, item.value, item.note, item.status || "normal", item.reference_range || ""));
    return rows.slice(0, 5);
  })();

  const isExpanded = height > 130;

  return (
    <div
      className={`summary-card visible ${isExpanded ? "expanded-overlay" : "pinned-compact"}`}
      style={{ height: `${height}px`, maxHeight: "480px" }}
    >
      <div className={`sc-header ${typeToneMap[docType] || "sc-tone-generic"}`}>
        <div className="sc-header-copy">
          <div className="sc-type-badge">{text.typeLabelMap[docType] || text.typeLabelMap.unknown}</div>
          <div className="sc-title">{analysis.doc_title || text.uploadedDocument}</div>
          <div className="sc-meta">
            <span className="sc-meta-pill">{highlights.length} {highlights.length === 1 ? text.highlightWord : text.highlightsWord}</span>
            <span className="sc-meta-pill">{text.readyForQuestions}</span>
          </div>
        </div>
      </div>

      <div className="sc-content-scroll">
        <div className="sc-summary-wrap">
          <div className="sc-summary-label">{text.summary}</div>
          <div className="sc-summary">{esc(displaySummary || text.fallbackSummary)}</div>
        </div>
        {isExpanded && docType === "medical" && medicalConclusion ? (
          <div className="sc-summary-wrap">
            <div className="sc-summary-label">{text.medicalConclusion}</div>
            <div className="sc-summary">{esc(medicalConclusion)}</div>
          </div>
        ) : null}
        {isExpanded && <HighlightsPanel rows={combinedImportantRows} text={text} />}
      </div>

      <div
        className="panel-resizer"
        onMouseDown={(e) => handleStartDrag(e.clientY)}
        onTouchStart={(e) => e.touches[0] && handleStartDrag(e.touches[0].clientY)}
        title="Drag down to expand summary overlay, drag up to collapse"
        role="slider"
        aria-valuenow={height}
        aria-valuemin={115}
        aria-valuemax={480}
        aria-label="Resize Analysis Panel"
        tabIndex={0}
      >
        <div className="resizer-handle-pill"><div className="resizer-line" /></div>
      </div>
    </div>
  );
}
