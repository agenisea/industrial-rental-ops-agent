import type { OrderSummaryInfo } from "@/types/api";
import { Row } from "./row";

interface SummaryBlockProps {
  summary: OrderSummaryInfo;
}

export function summaryBlockToText(summary: OrderSummaryInfo): string {
  const lines: string[] = [];
  lines.push(`Order: ${summary.code}`);
  lines.push(`Status: ${summary.status}`);
  lines.push(`Customer: ${summary.customer}`);
  lines.push(`Product: ${summary.product_name}`);
  if (summary.access_details) lines.push(`Access: ${summary.access_details}`);
  return lines.join("\n");
}

export function SummaryBlock({ summary }: SummaryBlockProps) {
  return (
    <div className="space-y-0.5">
      <Row label="Order" value={summary.code} />
      <Row label="Status" value={summary.status} />
      <Row label="Customer" value={summary.customer} />
      <Row label="Product" value={summary.product_name} />
      {summary.access_details && (
        <Row label="Access" value={summary.access_details} />
      )}
    </div>
  );
}
