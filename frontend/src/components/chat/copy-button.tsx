import { useState } from "react";
import { Copy, Check } from "lucide-react";

interface CopyButtonProps {
  getText: () => string;
}

export function CopyButton({ getText }: CopyButtonProps) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(getText());
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // clipboard write failed silently
    }
  }

  return (
    <button
      type="button"
      onClick={handleCopy}
      aria-label={copied ? "Copied" : "Copy chat"}
      className="rounded-md p-1.5 text-muted-foreground hover:bg-slate-100 active:scale-95 transition-all focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
    >
      {copied ? (
        <Check className="h-4 w-4 text-green-600" />
      ) : (
        <Copy className="h-4 w-4" />
      )}
    </button>
  );
}
