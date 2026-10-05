import { APIClient } from "../modules/api-client.js";
import { Validators } from "../utils/validators.js";

export function useUploadHandlers(state) {
  const {
    selectedFile,
    setSelectedFile,
    setFileStatus,
    selectedLanguage,
    setDocumentUploaded,
    setChunksCount,
    setAnalysis,
    setAnalysisCollapsed,
    setClarificationShownInSession,
    setMessages,
    setLoading,
    fileInputRef,
    showToast,
    ui,
    activeConversationId,
    setActiveConversationId,
    refreshConversations
  } = state;

  const onUploadZoneClick = () => {
    fileInputRef.current?.click();
  };

  const onFileSelected = (file) => {
    const validation = Validators.validateFile(file);
    if (validation) {
      showToast(validation, "error");
      return;
    }
    setSelectedFile(file);
    setFileStatus({ visible: true, name: file.name, meta: ui.app.readyToUpload });
  };

  const onUploadDocument = async () => {
    if (!selectedFile) {
      showToast(ui.app.chooseFileFirst, "error");
      return;
    }

    setLoading(true);
    setFileStatus({ visible: true, name: selectedFile.name, meta: ui.app.uploading });

    try {
      const result = await APIClient.uploadDocument(selectedFile, {
        language: selectedLanguage,
        conversationId: activeConversationId
      });
      setDocumentUploaded(true);
      if (result.conversationId && result.conversationId !== activeConversationId) {
        if (setActiveConversationId) setActiveConversationId(result.conversationId);
        if (refreshConversations) refreshConversations();
      }
      setChunksCount(String(result.chunks_created ?? 0));
      setFileStatus({
        visible: true,
        name: selectedFile.name,
        meta: `${result.chunks_created || 0} ${ui.app.sectionsIndexed}`,
      });
      setAnalysis(result.analysis || null);
      setAnalysisCollapsed(false);
      setClarificationShownInSession(false);
      setMessages([]);
      showToast(`${selectedFile.name} ${ui.app.uploadedSuccess}`, "success");
    } catch (error) {
      setFileStatus({ visible: true, name: selectedFile.name, meta: String(error?.message || ui.app.uploadFailed) });
      showToast(String(error?.message || ui.app.uploadFailed), "error");
    } finally {
      setLoading(false);
      setSelectedFile(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  return { onUploadZoneClick, onFileSelected, onUploadDocument };
}
