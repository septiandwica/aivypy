from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal

# ====== GENERATE ======
class QuestionRequest(BaseModel):
    track: Literal["career", "academic"] = Field(..., description="Assessment track")
    level: Literal["easy", "medium", "hard"] = "medium"
    count: int = 3

class MCQOption(BaseModel):
    key: str
    text: str

class MCQItem(BaseModel):
    id: str
    question: str
    options: List[MCQOption]
    answer: str
    competency_domain: str
    level: Literal["easy","medium","hard"]

class QuestionResponse(BaseModel):
    items: List[MCQItem]

# ====== SCORE / FEEDBACK ======
class AnswerItem(BaseModel):
    id: str
    answer: str

class ScoreRequest(BaseModel):
    track: Literal["career", "academic"]
    answers: List[AnswerItem]

class DomainFeedback(BaseModel):
    logic: Optional[str] = None
    creativity: Optional[str] = None
    interpersonal: Optional[str] = None
    practical: Optional[str] = None
    strategy: Optional[str] = None

class ScoredItem(BaseModel):
    id: str
    score: int
    feedback: str
    domain: Optional[str] = None

class ScoreResponse(BaseModel):
    overall_score: int
    items: List[ScoredItem]
    domain_feedback: DomainFeedback

# ====== ADAPTIVE ======
class AdaptiveRequest(BaseModel):
    track: Literal["career", "academic"]
    last_score: int
    last_level: Literal["easy","medium","hard"] = "medium"

class AdaptiveResponse(BaseModel):
    next_level: Literal["easy","medium","hard"]
    item: MCQItem

# ====== BEHAVIOR ======
class BehaviorRequest(BaseModel):
    response_times: List[float]  # in seconds
    consistency_score: int = 50  # 0-100
    interruptions: int = 0

class BehaviorResponse(BaseModel):
    attention_score: int
    processing_speed: int
    consistency: int

# ====== CAREER MATCH ======
class ProfileRequest(BaseModel):
    logic: int
    creativity: int
    interpersonal: int
    practical: int
    strategy: int

class CareerMatchResponse(BaseModel):
    major: str
    career: str
    rationale: str

# ====== VOICE EVAL ======
class VoiceRequest(BaseModel):
    transcript: str

class VoiceEvalResponse(BaseModel):
    confidence: int
    positivity: int
    empathy: int
    summary: str
