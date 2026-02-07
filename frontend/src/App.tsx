import { ChatWindow } from "@/components/chat/chat-window";

export default function App() {
  return (
    <div className="flex h-[100dvh] overflow-hidden items-center justify-center bg-background p-4">
      <ChatWindow />
    </div>
  );
}
