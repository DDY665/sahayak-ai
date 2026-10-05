export function esc(text) {
  return String(text ?? "");
}

export function looksNoisySummary(text) {
  const s = String(text || "").trim();
  if (!s) return true;
  const numbers = (s.match(/\d/g) || []).length;
  const words = s.split(/\s+/).filter(Boolean).length;
  if (numbers >= 24) return true;
  if (words > 120) return true;
  if ((s.match(/\//g) || []).length >= 6) return true;
  if ((s.match(/%/g) || []).length >= 5) return true;
  if (words > 45 && (s.match(/[.!?।]/g) || []).length <= 1) return true;
  return false;
}

export function inferUiDocType(analysis) {
  const declared = String(analysis?.doc_type || "").toLowerCase();
  if (["medical", "bank", "government"].includes(declared)) return declared;

  const points = Array.isArray(analysis?.important_points)
    ? analysis.important_points
    : Array.isArray(analysis?.important_details)
      ? analysis.important_details
      : [];
  const highlights = Array.isArray(analysis?.highlights) ? analysis.highlights : [];
  const summary = String(analysis?.summary || "").toLowerCase();

  const blob = [
    ...points.map((x) => `${x?.label || ""} ${x?.value || ""} ${x?.note || ""}`),
    ...highlights.map((x) => `${x?.name || ""} ${x?.value || ""} ${x?.note || ""}`),
    summary,
  ]
    .join(" ")
    .toLowerCase();

  if (/(medical|diagnosis|patient|hemoglobin|wbc|rbc|platelet|hba1c|glucose|creatinine|ecg|x-ray|ultrasound)/.test(blob)) {
    return "medical";
  }
  if (/(bank|loan|emi|interest|financial|penalty|statement|outstanding|dues|amount)/.test(blob)) {
    return "bank";
  }
  if (/(government|scheme|eligibility|benefit|application|deadline|notice)/.test(blob)) {
    return "government";
  }
  return "unknown";
}

export function buildReadableSummary(analysis, language) {
  const key = String(language || "English").toLowerCase();
  const docType = inferUiDocType(analysis);
  const dates = Array.isArray(analysis?.important_dates) ? analysis.important_dates : [];
  const points = Array.isArray(analysis?.important_points)
    ? analysis.important_points
    : Array.isArray(analysis?.important_details)
      ? analysis.important_details
      : [];
  const medicalConclusion = String(analysis?.medical_conclusion || "").trim();

  const topDate = String(dates[0]?.value || "").trim();
  const rawTopPoint = String(points[0]?.value || points[0]?.label || "").trim();
  const noisyPointTokens = new Set([
    "patient", "medical detail", "important date", "detail", "item", "document", "reference id", "ref"
  ]);
  const topPoint = noisyPointTokens.has(rawTopPoint.toLowerCase()) ? "" : rawTopPoint;

  if (key === "hindi") {
    if (docType === "medical") {
      return [
        "यह एक मेडिकल/लैब रिपोर्ट प्रतीत होती है।",
        medicalConclusion ? `मुख्य निष्कर्ष: ${medicalConclusion}` : "इसमें जांच से जुड़े परिणाम और स्वास्थ्य संकेत शामिल हैं।",
        topPoint ? `मुख्य बिंदु: ${topPoint}` : "रिपोर्ट का फोकस क्लिनिकल अवलोकन और मापदंडों पर है।",
        topDate ? `महत्वपूर्ण तिथि: ${topDate}` : "यह दस्तावेज़ आगे की समीक्षा के लिए उपयोगी है।"
      ].join(" ");
    }
    if (docType === "bank") {
      return [
        "यह एक बैंक/वित्तीय दस्तावेज़ प्रतीत होता है।",
        "इसका मुख्य फोकस राशि, भुगतान, देय तिथि या ब्याज संबंधी जानकारी पर है।",
        topPoint ? `मुख्य बिंदु: ${topPoint}` : "इसमें कुछ महत्वपूर्ण वित्तीय बिंदु हैं।",
        topDate ? `महत्वपूर्ण तिथि: ${topDate}` : "यह दस्तावेज़ निर्णय या कार्रवाई के लिए उपयोगी है।"
      ].join(" ");
    }
    return [
      "यह दस्तावेज़ महत्वपूर्ण जानकारी देता है।",
      "यह मुख्य रूप से दस्तावेज़ के विषय और जरूरी बिंदुओं को स्पष्ट करता है।",
      topPoint ? `मुख्य बिंदु: ${topPoint}` : "इसमें कुछ प्रमुख तथ्य शामिल हैं।",
      topDate ? `महत्वपूर्ण तिथि: ${topDate}` : "आवश्यक हो तो मैं इसे और स्पष्ट बिंदुओं में समझा सकता हूँ।"
    ].join(" ");
  }

  if (key === "telugu") {
    if (docType === "medical") {
      return [
        "ఇది ఒక వైద్య/ల్యాబ్ నివేదికగా కనిపిస్తోంది.",
        medicalConclusion ? `ముఖ్య నిర్ధారణ: ${medicalConclusion}` : "ఇందులో పరీక్ష ఫలితాలు మరియు ఆరోగ్య సూచనలు ఉన్నాయి.",
        topPoint ? `ముఖ్య అంశం: ${topPoint}` : "ఇది క్లినికల్ పరిశీలనలు మరియు కొలతలపై దృష్టి పెడుతుంది.",
        topDate ? `ముఖ్య తేదీ: ${topDate}` : "ఈ పత్రం తదుపరి సమీక్షకు ఉపయోగపడుతుంది."
      ].join(" ");
    }
    if (docType === "bank") {
      return [
        "ఇది ఒక బ్యాంకు/ఆర్థిక పత్రంగా కనిపిస్తోంది.",
        "ఇందులో మొత్తాలు, చెల్లింపులు, గడువులు లేదా వడ్డీకి సంబంధించిన సమాచారం ఉంటుంది.",
        topPoint ? `ముఖ్య అంశం: ${topPoint}` : "ఇందులో కొన్ని ముఖ్యమైన ఆర్థిక వివరాలు ఉన్నాయి.",
        topDate ? `ముఖ్య తేదీ: ${topDate}` : "ఇది చర్యలు తీసుకోవడానికి సహాయపడే సారాంశం."
      ].join(" ");
    }
    return [
      "ఈ పత్రంలో ముఖ్యమైన సమాచారం ఉంది.",
      "ఇది పత్రం యొక్క ప్రధాన విషయం మరియు కీలకాంశాలను స్పష్టంగా చూపిస్తుంది.",
      topPoint ? `ముఖ్య అంశం: ${topPoint}` : "ఇందులో కొన్ని ముఖ్యమైన విషయాలు ఉన్నాయి.",
      topDate ? `ముఖ్య తేదీ: ${topDate}` : "అవసరమైతే దీన్ని మరింత సులభంగా విభజించి వివరించగలను."
    ].join(" ");
  }

  if (docType === "medical") {
    return [
      "This appears to be a medical/lab report.",
      medicalConclusion ? `Main takeaway: ${medicalConclusion}` : "It contains test-related findings and clinical observations.",
      topPoint ? `Key point: ${topPoint}` : "The report focuses on measurable health indicators that may need interpretation.",
      topDate ? `Important date: ${topDate}` : "It is useful for follow-up clinical review."
    ].join(" ");
  }
  if (docType === "bank") {
    return [
      "This appears to be a bank/financial document.",
      "It mainly covers amounts, due timelines, and payment or interest obligations.",
      topPoint ? `Key point: ${topPoint}` : "It includes financially important details that should be tracked.",
      topDate ? `Important date: ${topDate}` : "It can guide next financial actions."
    ].join(" ");
  }
  return [
    "This document contains important information.",
    "It explains the main subject of the uploaded file and the details that matter most.",
    topPoint ? `Key point: ${topPoint}` : "It includes a few relevant points worth reviewing.",
    topDate ? `Important date: ${topDate}` : "It provides a practical overview for follow-up questions."
  ].join(" ");
}
