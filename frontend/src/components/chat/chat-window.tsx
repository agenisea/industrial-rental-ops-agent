import { useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MessageInput } from "./message-input";
import { MessageList } from "./message-list";
import { CopyButton } from "./copy-button";
import { useChat } from "@/hooks/use-chat";
import { formatChatTranscript } from "@/components/chat/agent-response";

export function ChatWindow() {
  const { messages, isLoading, sendMessage } = useChat();

  const getTranscript = useCallback(
    () => formatChatTranscript(messages),
    [messages]
  );

  return (
    <Card className="flex h-[700px] w-full max-w-2xl flex-col">
      <CardHeader className="flex-row items-center gap-3 border-b py-4">
        <span className="text-2xl" role="img" aria-label="Ops Agent">🏗️</span>
        <CardTitle className="flex-1 text-lg">Ops Agent</CardTitle>
        {messages.length > 0 && <CopyButton getText={getTranscript} />}
      </CardHeader>
      <CardContent className="flex flex-1 flex-col p-0 overflow-hidden">
        <MessageList messages={messages} />
        <MessageInput onSend={sendMessage} disabled={isLoading} />
      </CardContent>
    </Card>
  );
}
