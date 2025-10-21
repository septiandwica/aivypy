from fastapi import APIRouter, HTTPException
from models.schemas import AdaptiveRequest, AdaptiveResponse, MCQItem, MCQOption
from core.gemini_client import get_model
from models.utils import safe_json_parse, gen_id
import random

router = APIRouter(prefix="/adaptive", tags=["adaptive"])

PROMPT = """
You are an adaptive question generator for high school students’ {track} readiness.
Generate ONE multiple-choice question at {level} difficulty.
Return STRICT JSON ONLY:
{{
  "id": "string",
  "question": "string",
  "options": [
    {{"key":"A","text":"..."}},
    {{"key":"B","text":"..."}},
    {{"key":"C","text":"..."}},
    {{"key":"D","text":"..."}}
  ],
  "answer": "A|B|C|D",
  "competency_domain": "logic|creativity|interpersonal|practical|strategy",
  "level": "{level}"
}}
DO NOT include any commentary or markdown.
"""

@router.post("/next", response_model=AdaptiveResponse)
async def adaptive_next(req: AdaptiveRequest):
    """
    Returns the next adaptive item based on the last score and level.
    Simple rule-based logic:
    - If last_score > 80 → harder
    - If last_score < 50 → easier
    - Else → same level
    """
    # --- Determine next level ---
    next_level = req.last_level
    if req.last_score > 80 and req.last_level != "hard":
        next_level = "hard"
    elif req.last_score < 50 and req.last_level != "easy":
        next_level = "easy"
    elif 50 <= req.last_score <= 80:
        next_level = req.last_level  # keep the same

    # --- Generate item from Gemini ---
    model = get_model()
    prompt = PROMPT.format(track=req.track, level=next_level)
    res = model.generate_content(prompt)
    data = safe_json_parse(res.text, {})

    # --- Fallback if Gemini output messy ---
    try:
        item = MCQItem(
            id=data.get("id") or gen_id(),
            question=data.get("question", f"Example {next_level} question?"),
            options=[
                MCQOption(**opt)
                for opt in data.get(
                    "options",
                    [
                        {"key": "A", "text": "Option A"},
                        {"key": "B", "text": "Option B"},
                        {"key": "C", "text": "Option C"},
                        {"key": "D", "text": "Option D"},
                    ],
                )
            ],
            answer=data.get("answer", "A"),
            competency_domain=data.get(
                "competency_domain",
                random.choice(["logic", "creativity", "interpersonal", "practical", "strategy"]),
            ),
            level=next_level,
        )
    except Exception:
        raise HTTPException(500, "Failed to parse adaptive question.")

    return AdaptiveResponse(next_level=next_level, item=item)
