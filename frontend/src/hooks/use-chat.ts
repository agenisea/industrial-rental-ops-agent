import { useCallback, useRef, useState } from "react";
import { useSSEStream } from "@agenisea/sse-kit/client";
import type {
  ChatMessage,
  ChatRequest,
  ChatResponseEnvelope,
  StreamEvent,
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
    StreamEvent
  >({
    endpoint: "/api/chat",
    method: "POST",
    headers: { "Content-Type": "application/json" },
    initialEvent: "idle",
    completeEvent: "complete",
    errorEvent: "error",
    onUpdate: (_event, data) => {
      const id = assistantIdRef.current;
      if (_event === "thinking" || _event === "tool_call") {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === id ? { ...m, statusText: data.message } : m
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
