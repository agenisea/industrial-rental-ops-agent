import type { OrderInfo, SentimentInfo } from "@/types/api";
import { Row } from "./row";
import { FlaggedMessages } from "./flagged-messages";

interface OrderBlockProps {
  order: OrderInfo;
  sentiment?: SentimentInfo;
}

export function orderBlockToText(
  order: OrderInfo,
  sentiment?: SentimentInfo,
): string {
  const lines: string[] = [];
  lines.push(`Order: ${order.code}`);
  lines.push(`Status: ${order.status}`);
  lines.push(`Customer: ${order.customer}`);
  lines.push(`Product: ${order.product_name}`);
  lines.push(`Dates: ${order.start_date} \u2013 ${order.end_date}`);
  if (order.included_tonnage != null && order.included_tonnage > 0)
    lines.push(`Tonnage: ${order.included_tonnage} tons`);
  if (order.access_details) lines.push(`Access: ${order.access_details}`);
  if (sentiment) {
    lines.push(`Sentiment: ${sentiment.overall_sentiment}`);
    if (sentiment.flagged_messages.length > 0) {
      lines.push("Flagged:");
      for (const fm of sentiment.flagged_messages) {
        lines.push(`  \u201c${fm}\u201d`);
      }
    }
  }
  return lines.join("\n");
}

export function OrderBlock({ order, sentiment }: OrderBlockProps) {
  return (
    <div className="space-y-0.5">
      <Row label="Order" value={order.code} />
      <Row label="Status" value={order.status} />
      <Row label="Customer" value={order.customer} />
      <Row label="Product" value={order.product_name} />
      <Row
        label="Dates"
        value={`${order.start_date} \u2013 ${order.end_date}`}
      />
      {order.included_tonnage != null && order.included_tonnage > 0 && (
        <Row label="Tonnage" value={`${order.included_tonnage} tons`} />
      )}
      {order.access_details && (
        <Row label="Access" value={order.access_details} />
      )}
      {sentiment && (
        <>
          <Row label="Sentiment" value={sentiment.overall_sentiment} />
          <FlaggedMessages messages={sentiment.flagged_messages} />
        </>
      )}
    </div>
  );
}
