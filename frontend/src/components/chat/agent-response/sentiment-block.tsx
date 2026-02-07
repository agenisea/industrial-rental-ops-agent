import type { SentimentInfo } from "@/types/api";
import { Row } from "./row";
import { FlaggedMessages } from "./flagged-messages";

interface SentimentBlockProps {
  sentiment: SentimentInfo;
}

export function sentimentBlockToText(sentiment: SentimentInfo): string {
  const lines: string[] = [];
  lines.push(`Order: ${sentiment.order_code}`);
  lines.push(`Sentiment: ${sentiment.overall_sentiment}`);
  if (sentiment.flagged_messages.length > 0) {
    lines.push("Flagged:");
    for (const fm of sentiment.flagged_messages) {
      lines.push(`  \u201c${fm}\u201d`);
    }
  }
  return lines.join("\n");
}

export function SentimentBlock({ sentiment }: SentimentBlockProps) {
  return (
    <div className="space-y-0.5">
      <Row label="Order" value={sentiment.order_code} />
      <Row label="Sentiment" value={sentiment.overall_sentiment} />
      <FlaggedMessages messages={sentiment.flagged_messages} />
    </div>
  );
}
