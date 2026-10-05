import { getClarificationLocale } from "../i18n/strings.js";

export function toTitleCase(text) {
  return String(text || "")
    .toLowerCase()
    .replace(/\b\w/g, (m) => m.toUpperCase());
}

export function normalizeText(text) {
  return String(text || "").replace(/\s+/g, " ").trim();
}

export function normalizeLanguage(language) {
  return String(language || "English").toLowerCase();
}

export function createOption(label, prompt) {
  return { label: normalizeText(label), prompt: normalizeText(prompt) };
}

export function dedupeOptions(options) {
  return (Array.isArray(options) ? options : [])
    .filter((item) => item && item.label)
    .filter(
      (item, index, array) =>
        array.findIndex((x) => x.label.toLowerCase() === item.label.toLowerCase()) === index
    );
}

export function buildStapleOptions(language) {
  const locale = getClarificationLocale(language);
  return [
    createOption(locale.labels.quickSummary, locale.prompts.quickSummary),
    createOption(locale.labels.deadlines, locale.prompts.deadlines),
    createOption(locale.labels.risks, locale.prompts.risks),
  ];
}

export function buildDocumentSpecificOptions(analysis, language) {
  if (!analysis || typeof analysis !== "object") return [];

  const options = [];
  const locale = getClarificationLocale(language);
  const docType = String(analysis.doc_type || "").toLowerCase();
  const dates = Array.isArray(analysis.important_dates) ? analysis.important_dates : [];
  const medicalConclusion = String(analysis.medical_conclusion || "").trim();
  const points = Array.isArray(analysis.important_points)
    ? analysis.important_points
    : Array.isArray(analysis.important_details)
      ? analysis.important_details
      : [];
  const legacyMedical = Array.isArray(analysis.medical_details) ? analysis.medical_details : [];

  if (docType === "medical" || medicalConclusion || legacyMedical.length > 0) {
    options.push(createOption(locale.labels.medicalPrimary, locale.prompts.medicalPrimary));
  }

  if (docType === "bank") {
    options.push(createOption(locale.labels.bankPrimary, locale.prompts.bankPrimary));
  }

  if (docType === "government") {
    options.push(createOption(locale.labels.governmentPrimary, locale.prompts.governmentPrimary));
  }

  if (docType === "medical" || medicalConclusion || legacyMedical.length > 0) {
    options.push(createOption(locale.labels.medicalFlags, locale.prompts.medicalFlags));
  }

  if (docType === "bank") {
    options.push(createOption(locale.labels.bankAmounts, locale.prompts.bankAmounts));
  }

  if (docType === "government") {
    options.push(createOption(locale.labels.governmentEligibility, locale.prompts.governmentEligibility));
  }

  if (dates.length > 0) {
    const topDateLabel = normalizeText(dates[0]?.label || dates[0]?.value || "first deadline");
    options.push(
      createOption(
        locale.labels.dateFocus(toTitleCase(topDateLabel)),
        locale.prompts.dateFocus(topDateLabel)
      )
    );
  }

  if (points.length > 0) {
    const topDetail = normalizeText(points[0]?.label || points[0]?.value || "key point");
    options.push(
      createOption(
        locale.labels.keyPoint(toTitleCase(topDetail)),
        locale.prompts.keyPoint(topDetail)
      )
    );
  }

  return dedupeOptions(options).slice(0, 4);
}

export function parseClarificationPrompt(content, analysis, language) {
  if (typeof content !== "string") return null;

  const normalized = content.toLowerCase();
  const locale = getClarificationLocale(language);
  const hasClarificationIntent = (locale.markers || []).some((marker) =>
    normalized.includes(marker)
  );

  if (!hasClarificationIntent) return null;

  const staple = dedupeOptions(buildStapleOptions(language));
  const specific = dedupeOptions(buildDocumentSpecificOptions(analysis, language));

  const mixed = [...specific, ...staple]
    .slice(0, 4)
    .map((item, index) => ({ id: index + 1, label: item.label, prompt: item.prompt || item.label }));

  if (mixed.length === 0) return null;

  return {
    prompt: locale.prompt,
    options: mixed,
  };
}
