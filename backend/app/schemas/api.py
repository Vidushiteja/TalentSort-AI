from pydantic import BaseModel, Field, ConfigDict
from typing import Any

class JobCreate(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    department: str = ""
    description: str = Field(min_length=10)
    responsibilities: str = ""
    required_skills: list[str] = []
    preferred_skills: list[str] = []
    min_experience: float = Field(default=0, ge=0, le=60)
    education: str = ""
    certifications: list[str] = []
    weights: dict[str, float] = {"required":45,"preferred":20,"relevance":25,"experience":10}

class JobOut(JobCreate):
    id: int
    archived: bool
    model_config = ConfigDict(from_attributes=True)

class DecisionIn(BaseModel):
    decision: str
    note: str = ""

class NoteIn(BaseModel):
    note: str = Field(min_length=1, max_length=5000)
