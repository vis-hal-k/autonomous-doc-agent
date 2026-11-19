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
    insert_after_id: int | None = Field(default=None,description="For reviewer-added tasks only: id of the existing task this section should follow")
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
    ok: bool = Field(description="False if missing_tasks has any entry, True only if missing_tasks is empty")
    issues: list[str] = Field(default=[], description="Requirements from the request that no section covers")
    missing_tasks: list[Task] = Field(default=[] , description="One task per uncovered requirement. Empty list only if every requirement is covered") 


