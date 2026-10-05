export function getClarificationLocale(language) {
  const key = String(language || "English").toLowerCase();

  if (key === "hindi") {
    return {
      prompt: "सबसे अच्छा उत्तर देने के लिए, मुझे किस पर ध्यान देना चाहिए?",
      markers: ["aapko sabse useful answer", "aap kya chahte hain"],
      labels: {
        quickSummary: "त्वरित सारांश और मुख्य बातें",
        deadlines: "समय-सीमाएं और करने योग्य काम",
        risks: "जोखिम, दायित्व, और महत्वपूर्ण निर्णय",
        medicalPrimary: "मुख्य फोकस: गंभीर असामान्यताएं और अगले कदम",
        medicalFlags: "असामान्य जांचें और चिकित्सीय चेतावनियां",
        bankPrimary: "मुख्य फोकस: कुल वित्तीय देयता",
        bankAmounts: "राशियां, बकाया, और वित्तीय प्रभाव",
        governmentPrimary: "मुख्य फोकस: पात्रता और समय-सीमा की तैयारी",
        governmentEligibility: "पात्रता और आवश्यक दस्तावेज़",
        dateFocus: (label) => `महत्वपूर्ण तिथि पर ध्यान: ${label}`,
        keyPoint: (label) => `मुख्य बिंदु: ${label}`
      },
      prompts: {
        quickSummary: "इस दस्तावेज़ का संक्षिप्त सारांश दें और सबसे महत्वपूर्ण बातें बताएं।",
        deadlines: "सभी समय-सीमाएं और करने योग्य काम सूचीबद्ध करें, और बताएं कि किसे क्या करना है।",
        risks: "महत्वपूर्ण जोखिम, दायित्व, और जिन निर्णयों पर ध्यान देना चाहिए, उन्हें समझाएं।",
        medicalPrimary: "गंभीर असामान्यताओं, सीमा से बाहर परिणामों, और अगले चिकित्सा कदमों को प्राथमिकता दें।",
        medicalFlags: "असामान्य जांच, संदर्भ सीमा, और आगे की जांच की जरूरतों को उजागर करें।",
        bankPrimary: "कुल वित्तीय देयता को प्राथमिकता दें: मूलधन, ब्याज, दंड, देय तिथियां, और तत्काल भुगतान कदम।",
        bankAmounts: "सभी राशियों, बकाया, शुल्क, और कुल वित्तीय प्रभाव को निकालें।",
        governmentPrimary: "पात्रता आवश्यकताओं, छूटे दस्तावेज़ों, समय-सीमाओं, और अगले कदमों को प्राथमिकता दें।",
        governmentEligibility: "पात्रता नियम, आवश्यक दस्तावेज़, और आवेदन चरण समझाएं।",
        dateFocus: (label) => `इस दस्तावेज़ में महत्वपूर्ण तिथियों को समझाएं, शुरुआत ${label} से करें, और बताएं कि हर तिथि क्यों महत्वपूर्ण है।`,
        keyPoint: (label) => `इस दस्तावेज़ के मुख्य बिंदुओं को सरल शब्दों में समझाएं, जिसमें ${label} भी शामिल हो।`
      }
    };
  }

  if (key === "telugu") {
    return {
      prompt: "ఉత్తమ సమాధానం ఇవ్వడానికి, నేను ఏ విషయంపై దృష్టి పెట్టాలి?",
      markers: ["meeku accurate ga help", "meeku em kavali"],
      labels: {
        quickSummary: "త్వరిత సారాంశం మరియు ముఖ్య విషయాలు",
        deadlines: "గడువులు మరియు చేయాల్సిన పనులు",
        risks: "ప్రమాదాలు, బాధ్యతలు, మరియు ముఖ్య నిర్ణయాలు",
        medicalPrimary: "ప్రధాన దృష్టి: కీలక అసాధారణతలు మరియు తదుపరి చర్యలు",
        medicalFlags: "అసాధారణ పరీక్షలు మరియు వైద్య హెచ్చరికలు",
        bankPrimary: "ప్రధాన దృష్టి: మొత్తం ఆర్థిక బాధ్యత",
        bankAmounts: "మొత్తాలు, బకాయిలు, మరియు ఆర్థిక ప్రభావం",
        governmentPrimary: "ప్రధాన దృష్టి: అర్హత మరియు గడువు సిద్ధత",
        governmentEligibility: "అర్హత మరియు అవసరమైన పత్రాలు",
        dateFocus: (label) => `ముఖ్యమైన తేదీపై దృష్టి: ${label}`,
        keyPoint: (label) => `ముఖ్య అంశం: ${label}`
      },
      prompts: {
        quickSummary: "ఈ పత్రానికి సంక్షిప్త సారాంశం ఇవ్వండి మరియు అత్యంత ముఖ్యమైన విషయాలు చెప్పండి.",
        deadlines: "అన్ని గడువులు మరియు చేయాల్సిన పనులను జాబితా చేయండి, ఎవరు ఏమి చేయాలో చెప్పండి.",
        risks: "ముఖ్యమైన ప్రమాదాలు, బాధ్యతలు, మరియు దృష్టి పెట్టాల్సిన నిర్ణయాలను వివరించండి.",
        medicalPrimary: "కీలక అసాధారణతలు, రేంజ్ బయట ఫలితాలు, మరియు తదుపరి వైద్య చర్యలను ప్రాధాన్యం ఇవ్వండి.",
        medicalFlags: "అసాధారణ పరీక్షలు, సూచిక పరిధులు, మరియు ఫాలో-అప్ అవసరాలను చూపించండి.",
        bankPrimary: "మొత్తం ఆర్థిక బాధ్యతను ప్రాధాన్యం ఇవ్వండి: ప్రధాన మొత్తం, వడ్డీ, జరిమానాలు, గడువు తేదీలు, మరియు తక్షణ చెల్లింపు చర్యలు.",
        bankAmounts: "అన్ని మొత్తాలు, బకాయిలు, ఛార్జీలు, మరియు మొత్తం ఆర్థిక ప్రభావాన్ని వెలికితీయండి.",
        governmentPrimary: "అర్హత అవసరాలు, లోపించిన పత్రాలు, గడువులు, మరియు తదుపరి దశలను ప్రాధాన్యం ఇవ్వండి.",
        governmentEligibility: "అర్హత నియమాలు, అవసరమైన పత్రాలు, మరియు దరఖాస్తు దశలను వివరించండి.",
        dateFocus: (label) => `ఈ పత్రంలోని ముఖ్యమైన తేదీలను వివరించండి, మొదటిగా ${label}తో ప్రారంభించండి, మరియు ప్రతి తేదీ ఎందుకు ముఖ్యమో చెప్పండి.`,
        keyPoint: (label) => `ఈ పత్రంలోని ముఖ్య అంశాలను సులభంగా వివరించండి, ${label} సహా.`
      }
    };
  }

  return {
    prompt: "To give the best answer, what should I focus on?",
    markers: ["to give you the most accurate answer", "what do you want most from this document right now"],
    labels: {
      quickSummary: "Quick summary with top takeaways",
      deadlines: "Deadlines and action items",
      risks: "Risks, obligations, and key decisions",
      medicalPrimary: "Primary focus: critical abnormalities and next steps",
      medicalFlags: "Abnormal tests and medical flags",
      bankPrimary: "Primary focus: total financial liability",
      bankAmounts: "Amounts, dues, and financial impact",
      governmentPrimary: "Primary focus: eligibility and deadline readiness",
      governmentEligibility: "Eligibility and required documents",
      dateFocus: (label) => `Important date focus: ${label}`,
      keyPoint: (label) => `Key point: ${label}`
    },
    prompts: {
      quickSummary: "Give me a concise summary with the top takeaways and what matters most.",
      deadlines: "List all deadlines and action items with who needs to do what.",
      risks: "Explain important risks, obligations, and decisions I should pay attention to.",
      medicalPrimary: "Prioritize critical abnormalities, out-of-range results, and recommended next clinical steps.",
      medicalFlags: "Highlight abnormal tests, reference ranges, and what needs follow-up.",
      bankPrimary: "Prioritize total financial liability: principal, interest, penalties, due dates, and immediate payment actions.",
      bankAmounts: "Extract all amounts, dues, charges, and the overall financial impact.",
      governmentPrimary: "Prioritize eligibility requirements, missing documents, deadlines, and exact next submission steps.",
      governmentEligibility: "Explain the eligibility criteria and required documents in clear bullet points.",
      dateFocus: (label) => `Explain the important dates in this document, starting with ${label}, and why each one matters.`,
      keyPoint: (label) => `Explain the key points from this document, including ${label}, in simple terms.`
    }
  };
}
