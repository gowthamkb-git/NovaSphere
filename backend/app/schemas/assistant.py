from pydantic import BaseModel


class AskQuestionRequest(BaseModel):
    question: str
    department: str | None = None


class AskQuestionResponse(BaseModel):
    answer: str


class ChatRequest(BaseModel):
    question: str
    department: str | None = None
    session_id: str
    conversation_id: str | None = None


class ChatSource(BaseModel):
    source: str
    page: int | None = None


class ChatMessage(BaseModel):
    role: str
    content: str
    sources: list[ChatSource] = []
    created_at: str


class ConversationSummary(BaseModel):
    conversation_id: str
    title: str
    preview: str
    updated_at: str
    message_count: int


class ConversationDetail(BaseModel):
    conversation_id: str
    title: str
    updated_at: str
    messages: list[ChatMessage]


class ChatResponse(BaseModel):
    conversation_id: str
    answer: str
    sources: list[ChatSource]
