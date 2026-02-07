import type { OrderInfo, OrderSummaryInfo, SentimentInfo } from "@/types/api";
import { OrderBlock } from "./order-block";
import { SummaryBlock } from "./summary-block";
import { SentimentBlock } from "./sentiment-block";

export { formatChatTranscript } from "./format-transcript";

interface AgentStructuredResponseProps {
  orders?: OrderInfo[];
  order_summaries?: OrderSummaryInfo[];
  sentiment?: SentimentInfo;
}

export function AgentStructuredResponse({
  orders,
  order_summaries,
  sentiment,
}: AgentStructuredResponseProps) {
  const hasData =
    (orders && orders.length > 0) ||
    (order_summaries && order_summaries.length > 0) ||
    sentiment;

  if (!hasData) return null;

  const sentimentAttached =
    sentiment && orders?.some((o) => o.code === sentiment.order_code);

  return (
    <div className="mt-2 space-y-3 border-t border-border/50 pt-2 text-xs">
      {orders?.map((o) => (
        <OrderBlock
          key={o.code}
          order={o}
          sentiment={
            sentiment?.order_code === o.code ? sentiment : undefined
          }
        />
      ))}
      {order_summaries?.map((s) => (
        <SummaryBlock key={s.code} summary={s} />
      ))}
      {sentiment && !sentimentAttached && (
        <SentimentBlock sentiment={sentiment} />
      )}
    </div>
  );
}
