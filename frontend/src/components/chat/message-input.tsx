import { useState, useRef, type KeyboardEvent } from "react";
import { Button } from "@/components/ui/button";
import { SendHorizonal } from "lucide-react";

interface MessageInputProps {
  onSend: (text: string) => void;
  disabled?: boolean;
}

export function MessageInput({ onSend, disabled }: MessageInputProps) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  function handleSubmit() {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue("");
    textareaRef.current?.focus();
  }

  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  }

  return (
    <div className="flex gap-2 border-t p-4">
      <textarea
        id="chat-message"
        name="message"
        ref={textareaRef}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask about an order..."
        disabled={disabled}
        rows={1}
        className="flex-1 resize-none [field-sizing:content] max-h-32 overflow-y-auto rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:opacity-50"
      />
      <Button
        onClick={handleSubmit}
        disabled={disabled || !value.trim()}
        size="icon"
      >
        <SendHorizonal className="h-4 w-4" />
      </Button>
    </div>
  );
}
