from pydantic import BaseModel


class OrderInfo(BaseModel):
    code: str
    status: str
    customer: str
    product_name: str
    included_tonnage: float | None
    access_details: str
    start_date: str
    end_date: str


class OrderSummaryInfo(BaseModel):
    code: str
    status: str
    customer: str
    access_details: str
    product_name: str


class SentimentInfo(BaseModel):
    order_code: str
    overall_sentiment: str
    message_count: int
    positive: int
    neutral: int
    negative: int
    flagged_messages: list[str]


class AgentResponse(BaseModel):
    """Validated contract for every agent response."""

    message: str
    orders: list[OrderInfo] | None = None
    order_summaries: list[OrderSummaryInfo] | None = None
    sentiment: SentimentInfo | None = None
