from pydantic import BaseModel

from ops_agent.agent.schemas import AgentResponse


class ChatRequest(BaseModel):
    message: str


class ChatResponseEnvelope(BaseModel):
    data: AgentResponse
    request_id: str
    model: str
