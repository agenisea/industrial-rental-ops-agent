import type { ChatMessage } from "@/types/api";
import { orderBlockToText } from "./order-block";
import { summaryBlockToText } from "./summary-block";
import { sentimentBlockToText } from "./sentiment-block";

export function formatChatTranscript(messages: ChatMessage[]): string {
  return messages
    .filter(
      (m) =>
        m.content ||
        m.orders?.length ||
        m.order_summaries?.length ||
        m.sentiment,
    )
    .map((m) => {
      const role = m.role === "user" ? "User" : "Agent";
      const parts: string[] = [];
      if (m.content) parts.push(`${role}: ${m.content}`);

      const sentimentAttached =
        m.sentiment &&
        m.orders?.some((o) => o.code === m.sentiment!.order_code);

      if (m.orders?.length) {
        for (const o of m.orders) {
          const attached =
            m.sentiment?.order_code === o.code ? m.sentiment : undefined;
          parts.push(orderBlockToText(o, attached));
        }
      }
      if (m.order_summaries?.length) {
        for (const s of m.order_summaries) {
          parts.push(summaryBlockToText(s));
        }
      }
      if (m.sentiment && !sentimentAttached) {
        parts.push(sentimentBlockToText(m.sentiment));
      }
      return parts.join("\n\n");
    })
    .join("\n\n---\n\n");
}
