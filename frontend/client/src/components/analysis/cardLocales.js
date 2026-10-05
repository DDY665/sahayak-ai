export function getCardText(language) {
  const key = String(language || "English").toLowerCase();

  if (key === "hindi") {
    return {
      typeLabelMap: {
        medical: "मेडिकल रिपोर्ट",
        bank: "बैंक / लोन दस्तावेज",
        government: "सरकारी योजना",
        unknown: "दस्तावेज"
      },
      uploadedDocument: "अपलोड किया गया दस्तावेज",
      highlightWord: "हाइलाइट",
      highlightsWord: "हाइलाइट्स",
      readyForQuestions: "प्रश्नों के लिए तैयार",
      expandAnalysis: "विश्लेषण खोलें",
      collapseAnalysis: "विश्लेषण समेटें",
      expand: "खोलें",
      collapse: "समेटें",
      crux: "सार",
      summary: "सारांश",
      importantDates: "महत्वपूर्ण तिथियां / डेडलाइन",
      medicalConclusion: "मेडिकल निष्कर्ष",
      importantPoints: "महत्वपूर्ण बिंदु",
      date: "तारीख",
      medical: "मेडिकल",
      detail: "विवरण",
      item: "आइटम",
      ref: "रेफ",
      fallbackSummary: "दस्तावेज सफलतापूर्वक अपलोड हो गया है।",
      noHighlights: "इस दस्तावेज से संरचित हाइलाइट्स नहीं निकाले जा सके।",
      statusMap: {
        normal: "सामान्य",
        high: "उच्च",
        low: "कम",
        warning: "चेतावनी",
        attention: "ध्यान दें",
        important: "महत्वपूर्ण",
        deadline: "अंतिम तिथि"
      }
    };
  }

  if (key === "telugu") {
    return {
      typeLabelMap: {
        medical: "వైద్య నివేదిక",
        bank: "బ్యాంక్ / రుణ పత్రం",
        government: "ప్రభుత్వ పథకం",
        unknown: "పత్రం"
      },
      uploadedDocument: "అప్‌లోడ్ చేసిన పత్రం",
      highlightWord: "హైలైట్",
      highlightsWord: "హైలైట్స్",
      readyForQuestions: "ప్రశ్నలకు సిద్ధంగా ఉంది",
      expandAnalysis: "విశ్లేషణను విస్తరించండి",
      collapseAnalysis: "విశ్లేషణను మడతపెట్టండి",
      expand: "విస్తరించు",
      collapse: "మడతపెట్టు",
      crux: "సారం",
      summary: "సంక్షిప్తం",
      importantDates: "ముఖ్యమైన తేదీలు / గడువులు",
      medicalConclusion: "వైద్య నిర్ధారణ",
      importantPoints: "ముఖ్యమైన అంశాలు",
      date: "తేదీ",
      medical: "వైద్య",
      detail: "వివరం",
      item: "అంశం",
      ref: "రిఫ్",
      fallbackSummary: "పత్రం విజయవంతంగా అప్‌లోడ్ చేయబడింది.",
      noHighlights: "ఈ పత్రం నుండి నిర్మిత హైలైట్స్‌ను తీసుకోలేకపోయాం.",
      statusMap: {
        normal: "సాధారణం",
        high: "ఎక్కువ",
        low: "తక్కువ",
        warning: "హెచ్చరిక",
        attention: "శ్రద్ధ",
        important: "ముఖ్యం",
        deadline: "గడువు"
      }
    };
  }

  return {
    typeLabelMap: {
      medical: "Medical Report",
      bank: "Bank / Loan Document",
      government: "Government Scheme",
      unknown: "Document"
    },
    uploadedDocument: "Uploaded Document",
    highlightWord: "highlight",
    highlightsWord: "highlights",
    readyForQuestions: "Ready for questions",
    expandAnalysis: "Expand analysis",
    collapseAnalysis: "Collapse analysis",
    expand: "Expand",
    collapse: "Collapse",
    crux: "Crux",
    summary: "Summary",
    importantDates: "Important Dates / Deadlines",
    medicalConclusion: "Medical Conclusion",
    importantPoints: "Important Points",
    date: "Date",
    medical: "Medical",
    detail: "Detail",
    item: "Item",
    ref: "Ref",
    fallbackSummary: "Document uploaded successfully.",
    noHighlights: "No structured highlights could be extracted from this document.",
    statusMap: {
      normal: "normal",
      high: "high",
      low: "low",
      warning: "warning",
      attention: "attention",
      important: "important",
      deadline: "deadline"
    }
  };
}
