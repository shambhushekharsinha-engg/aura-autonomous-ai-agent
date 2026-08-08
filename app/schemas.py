from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Persona(BaseModel):
    name: str
    domain: str

class InitRequest(BaseModel):
    persona: Persona

class InitResponse(BaseModel):
    agentId: str

class PostResponse(BaseModel):
    id: str
    createdAt: str  # Send as ISO 8601 string
    text: str
    rationale: str
    stance: Optional[str] = None
    sources: List[str]

class FeedResponse(BaseModel):
    posts: List[PostResponse]
