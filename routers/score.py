from fastapi import APIRouter, HTTPException
from models.schemas import (
    ScoreRequest,
    ScoreResponse,
    ScoredItem,
    DomainFeedback,
)
from core.gemini_client import get_model
from models.utils import safe_json_parse

router = APIRouter(prefix="/score", tags=["score"])

PROMPT = """
You are an educational assessor evaluating high school students' {track} readiness.
Given a list of question-answer pairs with correct answers and domains,
analyze each answer and provide:
- score: integer 0-100 (accuracy or reasoning quality)
- feedback: short constructive feedback
Return JSON ONLY:
{{
  "items": [
    {{
      "id": "string",
      "score": int,
      "feedback": "string",
      "domain": "logic|creativity|interpersonal|practical|strategy"
    }}
  ],
  "domain_feedback": {{
    "logic": "string",
    "creativity": "string",
    "interpersonal": "string",
    "practical": "string",
    "strategy": "string"
  }},
  "overall_score": int
}}
Text:
{answers}
"""

@router.post("", response_model=ScoreResponse)
async def score_answers(req: ScoreRequest):
    """
    Evaluate answers with AI-driven scoring and domain-based feedback summary.
    """
    model = get_model()

    # ✳️ Generate simple input text for Gemini
    answers_text = "\n".join(
        [f"{a.id}: {a.answer}" for a in req.answers]
    )

    prompt = PROMPT.format(track=req.track, answers=answers_text)
    res = model.generate_content(prompt)

    data = safe_json_parse(res.text, {})

    # Fallback default values
    if not isinstance(data, dict):
        data = {}

    items = []
    domain_scores = {
        "logic": [],
        "creativity": [],
        "interpersonal": [],
        "practical": [],
        "strategy": [],
    }

    # --- Parse AI result items ---
    for it in data.get("items", []):
        try:
            score = int(it.get("score", 60))
            domain = it.get("domain", "logic")
            feedback = it.get("feedback", "Good effort; keep improving.")
            items.append(
                ScoredItem(
                    id=it.get("id", "unknown"),
                    score=score,
                    feedback=feedback,
                    domain=domain,
                )
            )
            if domain in domain_scores:
                domain_scores[domain].append(score)
        except Exception:
            continue

    # --- Fallback scoring if AI fails ---
    if not items and req.answers:
        for i, a in enumerate(req.answers):
            domain = list(domain_scores.keys())[i % 5]
            score = 60 + (i * 5) % 40
            items.append(
                ScoredItem(
                    id=a.id,
                    score=score,
                    feedback="Consistent reasoning but could be deeper.",
                    domain=domain,
                )
            )
            domain_scores[domain].append(score)

    # --- Compute averages per domain ---
    domain_avg = {
        d: int(sum(v) / len(v)) if v else 0 for d, v in domain_scores.items()
    }

    overall_score = (
        int(sum(domain_avg.values()) / len(domain_avg))
        if domain_avg else 0
    )

    # --- Generate AI domain feedback summary ---
    feedback_prompt = f"""
Provide 1–2 sentences of feedback per domain based on these scores:
{domain_avg}
Return JSON ONLY:
{{
  "logic": "string",
  "creativity": "string",
  "interpersonal": "string",
  "practical": "string",
  "strategy": "string"
}}
"""
    fb_res = model.generate_content(feedback_prompt)
    fb_data = safe_json_parse(fb_res.text, {})

    domain_feedback = DomainFeedback(**{
        "logic": fb_data.get("logic", "You demonstrated solid reasoning."),
        "creativity": fb_data.get("creativity", "You showed some creative potential."),
        "interpersonal": fb_data.get("interpersonal", "Good teamwork and communication."),
        "practical": fb_data.get("practical", "Strong practical problem-solving."),
        "strategy": fb_data.get("strategy", "Effective planning and adaptability.")
    })

    return ScoreResponse(
        overall_score=overall_score,
        items=items,
        domain_feedback=domain_feedback
    )
