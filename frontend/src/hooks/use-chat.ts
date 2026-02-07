import { useCallback, useRef, useState } from "react";
import { useSSEStream } from "@agenisea/sse-kit/client";
import type {
  ChatMessage,
  ChatRequest,
  ChatResponseEnvelope,
  StreamPhase,
  StreamUpdate,
} from "@/types/api";

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const assistantIdRef = useRef<string>("");
  const idCounterRef = useRef(0);

  const nextId = useCallback(() => `msg-${++idCounterRef.current}`, []);

  const { state, start } = useSSEStream<
    ChatRequest,
    ChatResponseEnvelope,
    StreamUpdate,
    StreamPhase
  >({
    endpoint: "/api/chat",
    method: "POST",
    headers: { "Content-Type": "application/json" },
    initialPhase: "idle",
    completePhase: "complete",
    errorPhase: "error",
    extractResult: (update) => update.result,
    extractError: (update) => update.error,
    isComplete: (update) => update.phase === "complete",
    isError: (update) => update.phase === "error",
    onUpdate: (update) => {
      const id = assistantIdRef.current;
      if (update.phase === "thinking" || update.phase === "tool_call") {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === id ? { ...m, statusText: update.message } : m
          )
        );
      }
    },
    onComplete: (envelope) => {
      const id = assistantIdRef.current;
      const { message, orders, order_summaries, sentiment } = envelope.data;
      setMessages((prev) =>
        prev.map((m) =>
          m.id === id
            ? {
                ...m,
                content: message,
                orders: orders ?? undefined,
                order_summaries: order_summaries ?? undefined,
                sentiment: sentiment ?? undefined,
                isLoading: false,
                statusText: undefined,
              }
            : m
        )
      );
    },
    onError: () => {
      const id = assistantIdRef.current;
      setMessages((prev) =>
        prev.map((m) =>
          m.id === id
            ? {
                ...m,
                content: "Something went wrong. Please try again.",
                isLoading: false,
                statusText: undefined,
              }
            : m
        )
      );
    },
  });

  const sendMessage = useCallback(
    async (text: string) => {
      const userMsg: ChatMessage = {
        id: nextId(),
        role: "user",
        content: text,
      };
      const assistantId = nextId();
      assistantIdRef.current = assistantId;

      const loadingMsg: ChatMessage = {
        id: assistantId,
        role: "assistant",
        content: "",
        isLoading: true,
      };

      setMessages((prev) => [...prev, userMsg, loadingMsg]);
      await start({ message: text });
    },
    [start]
  );

  return {
    messages,
    isLoading: state.isStreaming,
    sendMessage,
  };
}
