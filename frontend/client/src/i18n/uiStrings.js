export function getUIStrings(language) {
  const key = String(language || "English").toLowerCase();

  if (key === "hindi") {
    return {
      app: {
        readyToUpload: "अपलोड के लिए तैयार",
        uploading: "अपलोड हो रहा है...",
        sectionsIndexed: "सेक्शन इंडेक्स किए गए",
        uploadedSuccess: "सफलतापूर्वक अपलोड हुआ",
        chooseFileFirst: "पहले फाइल चुनें",
        uploadFailed: "अपलोड विफल हुआ",
        uploadDocumentFirst: "पहले दस्तावेज़ अपलोड करें",
        cannotReachServer: "सर्वर से कनेक्ट नहीं हो सका",
        emptyQuestion: "प्रश्न खाली नहीं हो सकता",
        noResponse: "कोई उत्तर जनरेट नहीं हुआ।",
        streamFailed: "स्ट्रीमिंग विफल हुई",
        voiceUnsupported: "इस ब्राउज़र में वॉइस इनपुट समर्थित नहीं है"
      },
      header: { dark: "डार्क", light: "लाइट", toggleTheme: "थीम बदलें", serverOnline: "सर्वर ऑनलाइन", serverOffline: "सर्वर ऑफलाइन" },
      sidebar: { document: "दस्तावेज़", uploadDocument: "दस्तावेज़ अपलोड करें", uploading: "अपलोड हो रहा है...", uploadSubtext: "PDF, TXT, DOC (अधिकतम 15MB)", language: "भाषा", documentInfo: "दस्तावेज़ जानकारी", sectionsIndexed: "सेक्शन इंडेक्स किए गए" },
      chat: { emptyTitle: "शुरू करने के लिए दस्तावेज़ अपलोड करें", emptyDesc: "आपके दस्तावेज़ का विश्लेषण और इंडेक्सिंग तुरंत प्रश्नोत्तर के लिए की जाएगी", suggestions: ["इस दस्तावेज़ में क्या है?", "मुख्य बिंदुओं का सारांश दें", "महत्वपूर्ण तिथियां बताएं"], you: "आप", ai: "AI", basedOn: "आधार", source: "स्रोत", sources: "स्रोत" },
      composer: { pickerHelp: "↑↓ नेविगेट करें · Enter से चुनें · Esc से स्किप करें", skip: "स्किप", skipClarification: "स्पष्टीकरण छोड़ें", askPlaceholder: "प्रश्न पूछें, या बोलने के लिए टैप करें।", voiceInput: "वॉइस इनपुट", sendMessage: "संदेश भेजें", inputHint: "भेजने के लिए Enter दबाएं · नई लाइन के लिए Shift+Enter" },
      fileInputLabel: "दस्तावेज़ अपलोड करें"
    };
  }

  if (key === "telugu") {
    return {
      app: {
        readyToUpload: "అప్‌లోడ్‌కు సిద్ధం",
        uploading: "అప్‌లోడ్ అవుతోంది...",
        sectionsIndexed: "విభాగాలు సూచీకరించబడ్డాయి",
        uploadedSuccess: "విజయవంతంగా అప్‌లోడ్ అయింది",
        chooseFileFirst: "ముందు ఫైల్ ఎంచుకోండి",
        uploadFailed: "అప్‌లోడ్ విఫలమైంది",
        uploadDocumentFirst: "ముందుగా పత్రాన్ని అప్‌లోడ్ చేయండి",
        cannotReachServer: "సర్వర్‌ను చేరుకోలేకపోయాము",
        emptyQuestion: "ప్రశ్న ఖాళీగా ఉండకూడదు",
        noResponse: "స్పందన తయారు కాలేదు.",
        streamFailed: "స్ట్రీమింగ్ విఫలమైంది",
        voiceUnsupported: "ఈ బ్రౌజర్‌లో వాయిస్ ఇన్‌పుట్‌కు మద్దతు లేదు"
      },
      header: { dark: "డార్క్", light: "లైట్", toggleTheme: "థీమ్ మార్చు", serverOnline: "సర్వర్ ఆన్‌లైన్", serverOffline: "సర్వర్ ఆఫ్‌లైన్" },
      sidebar: { document: "పత్రం", uploadDocument: "పత్రాన్ని అప్‌లోడ్ చేయండి", uploading: "అప్‌లోడ్ అవుతోంది...", uploadSubtext: "PDF, TXT, DOC (గరిష్ఠం 15MB)", language: "భాష", documentInfo: "పత్ర సమాచారం", sectionsIndexed: "విభాగాలు సూచీకరించబడ్డాయి" },
      chat: { emptyTitle: "ప్రారంభించడానికి పత్రాన్ని అప్‌లోడ్ చేయండి", emptyDesc: "తక్షణ ప్రశ్నోత్తరాల కోసం మీ పత్రాన్ని విశ్లేషించి సూచీకరించబడుతుంది", suggestions: ["ఈ పత్రంలో ఏముంది?", "ముఖ్యాంశాలను సంక్షిప్తంగా చెప్పండి", "ముఖ్యమైన తేదీలు కనుగొనండి"], you: "మీరు", ai: "AI", basedOn: "ఆధారం", source: "మూలం", sources: "మూలాలు" },
      composer: { pickerHelp: "↑↓ తో నావిగేట్ చేయండి · Enter తో ఎంచుకోండి · Esc తో దాటవేయండి", skip: "దాటవేయి", skipClarification: "స్పష్టీకరణను దాటవేయి", askPlaceholder: "ప్రశ్న అడగండి, లేదా మాట్లాడేందుకు ట్యాప్ చేయండి.", voiceInput: "వాయిస్ ఇన్‌పుట్", sendMessage: "సందేశం పంపు", inputHint: "పంపడానికి Enter నొక్కండి · కొత్త లైన్ కోసం Shift+Enter" },
      fileInputLabel: "పత్రాన్ని అప్‌లోడ్ చేయండి"
    };
  }

  return {
    app: { readyToUpload: "Ready to upload", uploading: "Uploading...", sectionsIndexed: "sections indexed", uploadedSuccess: "successfully uploaded", chooseFileFirst: "Please choose a file first", uploadFailed: "Upload failed", uploadDocumentFirst: "Please upload a document first", cannotReachServer: "Could not reach server", emptyQuestion: "Question cannot be empty", noResponse: "No response generated.", streamFailed: "Streaming failed", voiceUnsupported: "Voice input is not supported in this browser" },
    header: { dark: "Dark", light: "Light", toggleTheme: "Toggle theme", serverOnline: "Server online", serverOffline: "Server offline" },
    sidebar: { document: "Document", uploadDocument: "Upload Document", uploading: "Uploading...", uploadSubtext: "PDF, TXT, DOC (max 15MB)", language: "Language", documentInfo: "Document Info", sectionsIndexed: "Sections indexed" },
    chat: { emptyTitle: "Upload a document to begin", emptyDesc: "Your document will be analyzed and indexed for instant Q&A", suggestions: ["What's in this document?", "Summarize key points", "Find important dates"], you: "You", ai: "AI", basedOn: "Based on", source: "source", sources: "sources" },
    composer: { pickerHelp: "↑↓ to navigate · Enter to select · Esc to skip", skip: "Skip", skipClarification: "Skip clarification", askPlaceholder: "Ask a question, or tap to speak.", voiceInput: "Voice input", sendMessage: "Send message", inputHint: "Press Enter to send · Shift+Enter for new line" },
    fileInputLabel: "Upload document"
  };
}
