from typing import Optional
from pydantic import BaseModel, Field


class TestCase(BaseModel):
    input: str
    expected_output: str


class QuestionCreate(BaseModel):
    title: str
    description: str
    difficulty: str = Field(pattern="^(easy|medium|hard)$")
    tags: list[str] = []
    topic: str  # e.g. "Arrays" — must match a node in the topic dependency graph
    test_cases: list[TestCase]


class QuestionOut(BaseModel):
    id: str
    title: str
    description: str
    difficulty: str
    tags: list[str]
    topic: str
    # test_cases intentionally omitted from list/detail views so users can't read expected outputs


class QuestionAdminOut(QuestionOut):
    test_cases: list[TestCase]


class SubmitCode(BaseModel):
    question_id: str
    code: str
    contest_id: Optional[int] = None


class SubmissionResult(BaseModel):
    verdict: str
    runtime_ms: Optional[float]
    passed_cases: int
    total_cases: int
