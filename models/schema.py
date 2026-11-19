from typing import Any, Literal, Optional

from pydantic import BaseModel, Field 

class AgentRequest(BaseModel):

    request: str = Field(
        ...,
        min_length=5,
        description="Natural language instruction for the AI agent"
    )

class Task(BaseModel):
    id: int
    title: str
    instructions: str = Field(description="What this section should cover")
    status: Literal["pending", "done", "failed"] = "pending"


class Plan(BaseModel):
    document_type: str
    title: str
    assumptions: list[str] = Field(description="Assumptions made for missing or ambiguous info")
    tasks: list[Task]

class SectionContent(BaseModel):
    heading: str
    paragraphs: list[str]
    bullets: list[str] = []


class Review(BaseModel):
    ok: bool
    issues: list[str] = []
    missing_tasks: list[Task] = []

