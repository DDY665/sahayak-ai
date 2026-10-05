import { useUploadHandlers } from "./useUploadHandlers.js";
import { useChatHandlers } from "./useChatHandlers.js";

export function useAppHandlers(state) {
  const uploadHandlers = useUploadHandlers(state);
  const chatHandlers = useChatHandlers(state);

  return {
    ...uploadHandlers,
    ...chatHandlers,
  };
}
