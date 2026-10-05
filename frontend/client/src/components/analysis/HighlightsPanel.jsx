import { esc } from "./cardHelpers.js";

export default function HighlightsPanel({ rows, text }) {
  if (!rows || rows.length === 0) {
    return <p className="sc-empty">{text.noHighlights}</p>;
  }

  return (
    <div className="sc-highlights">
      {rows.map((item, idx) => {
        const status = String(item.status || "normal").toLowerCase();
        const statusLabel = text.statusMap[status] || status;
        return (
          <article className="sc-row" key={`h-${idx}`}>
            <div className="sc-row-left">
              <span className={`sc-dot sc-dot-${status}`} />
              <div className="sc-row-body">
                <div className="sc-row-name">{esc(item.name || text.item)}</div>
                <div className="sc-row-note">{esc(item.note || "")}</div>
              </div>
            </div>
            <div className="sc-row-right">
              <span className="sc-value">{esc(item.value || "")}</span>
              {item.reference_range ? (
                <span className="sc-ref">{text.ref}: {esc(item.reference_range)}</span>
              ) : null}
              <span className={`sc-badge sc-badge-${status}`}>{statusLabel}</span>
            </div>
          </article>
        );
      })}
    </div>
  );
}
