export interface ChatRequest {
  message: string;
}

export interface AgentResponse {
  message: string;
  orders?: OrderInfo[] | null;
  order_summaries?: OrderSummaryInfo[] | null;
  sentiment?: SentimentInfo | null;
}

export interface OrderInfo {
  code: string;
  status: string;
  customer: string;
  product_name: string;
  included_tonnage: number | null;
  access_details: string;
  start_date: string;
  end_date: string;
}

export interface OrderSummaryInfo {
  code: string;
  status: string;
  customer: string;
  access_details: string;
  product_name: string;
}

export interface SentimentInfo {
  order_code: string;
  overall_sentiment: string;
  message_count: number;
  positive: number;
  neutral: number;
  negative: number;
  flagged_messages: string[];
}

export interface ChatResponseEnvelope {
  data: AgentResponse;
  request_id: string;
  model: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  isLoading?: boolean;
  statusText?: string;
  orders?: OrderInfo[];
  order_summaries?: OrderSummaryInfo[];
  sentiment?: SentimentInfo;
}

export type StreamPhase =
  | "idle"
  | "thinking"
  | "tool_call"
  | "complete"
  | "error";

export interface StreamUpdate {
  phase: StreamPhase;
  message?: string;
  result?: ChatResponseEnvelope;
  error?: string;
}
