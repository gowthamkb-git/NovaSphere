from pydantic import BaseModel


class IngestionResponse(BaseModel):
    status: str
    inserted_documents: int
