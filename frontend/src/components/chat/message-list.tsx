import { useEffect, useRef } from "react";
import { cn } from "@/lib/utils";
import { Skeleton } from "@/components/ui/skeleton";
import type { ChatMessage } from "@/types/api";
import { Bot, User } from "lucide-react";
import { AgentStructuredResponse } from "@/components/chat/agent-response";
import { ErrorBoundary } from "@/components/chat/agent-response/error-boundary";

interface MessageListProps {
  messages: ChatMessage[];
}

export function MessageList({ messages }: MessageListProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = containerRef.current;
    if (el) {
      el.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
    }
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="flex flex-1 items-center justify-center text-muted-foreground">
        <div className="text-center">
          <Bot className="mx-auto mb-3 h-10 w-10 opacity-40" />
          <p className="text-sm font-medium">Ops Agent</p>
          <p className="mt-1 text-xs">
            Ask about orders, active rentals, or customer sentiment.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div ref={containerRef} className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.map((msg) => (
        <div
          key={msg.id}
          className={cn(
            "flex gap-3",
            msg.role === "user" ? "justify-end" : "justify-start"
          )}
        >
          {msg.role === "assistant" && (
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10">
              <Bot className="h-4 w-4 text-primary" />
            </div>
          )}
          <div
            className={cn(
              "max-w-[80%] rounded-lg px-4 py-2 text-sm",
              msg.role === "user"
                ? "bg-primary text-primary-foreground"
                : "bg-muted"
            )}
          >
            {msg.isLoading ? (
              <div
                role="status"
                aria-busy="true"
                aria-live="polite"
              >
                {msg.statusText ? (
                  <p className="text-sm text-muted-foreground animate-pulse">
                    {msg.statusText}
                  </p>
                ) : (
                  <div className="space-y-2">
                    <Skeleton className="h-3 w-48" />
                    <Skeleton className="h-3 w-36" />
                  </div>
                )}
                <span className="sr-only">Loading response</span>
              </div>
            ) : (
              <>
                {msg.content && (
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                )}
                <ErrorBoundary>
                  <AgentStructuredResponse
                    orders={msg.orders}
                    order_summaries={msg.order_summaries}
                    sentiment={msg.sentiment}
                  />
                </ErrorBoundary>
              </>
            )}
          </div>
          {msg.role === "user" && (
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-secondary">
              <User className="h-4 w-4 text-secondary-foreground" />
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
