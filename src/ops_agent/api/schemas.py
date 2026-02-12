from pydantic import BaseModel

from ops_agent.schemas import OrderInfo, OrderSummaryInfo, SentimentInfo


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    message: str
    orders: list[OrderInfo] | None = None
    order_summaries: list[OrderSummaryInfo] | None = None
    sentiment: SentimentInfo | None = None
