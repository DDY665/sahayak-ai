// Drag-to-resize logic for the AnalysisCard panel
import { useEffect, useRef, useState } from "react";

export function useAnalysisDrag(onHeightChange) {
  const [height, setHeight] = useState(115);
  const isDraggingRef = useRef(false);
  const startYRef = useRef(0);
  const startHeightRef = useRef(115);

  useEffect(() => {
    onHeightChange?.(height);
  }, [height, onHeightChange]);

  useEffect(() => {
    const clamp = (val) => Math.max(115, Math.min(480, val));

    const handleMouseMove = (e) => {
      if (!isDraggingRef.current) return;
      setHeight(clamp(startHeightRef.current + (e.clientY - startYRef.current)));
    };

    const handleMouseUp = () => {
      if (isDraggingRef.current) {
        isDraggingRef.current = false;
        document.body.style.cursor = "";
        document.body.style.userSelect = "";
      }
    };

    const handleTouchMove = (e) => {
      if (!isDraggingRef.current || !e.touches[0]) return;
      setHeight(clamp(startHeightRef.current + (e.touches[0].clientY - startYRef.current)));
    };

    const handleTouchEnd = () => {
      if (isDraggingRef.current) {
        isDraggingRef.current = false;
        document.body.style.cursor = "";
        document.body.style.userSelect = "";
      }
    };

    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseup", handleMouseUp);
    window.addEventListener("touchmove", handleTouchMove);
    window.addEventListener("touchend", handleTouchEnd);

    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
      window.removeEventListener("touchmove", handleTouchMove);
      window.removeEventListener("touchend", handleTouchEnd);
    };
  }, []);

  const handleStartDrag = (clientY) => {
    isDraggingRef.current = true;
    startYRef.current = clientY;
    startHeightRef.current = height;
    document.body.style.cursor = "row-resize";
    document.body.style.userSelect = "none";
  };

  return { height, handleStartDrag };
}
