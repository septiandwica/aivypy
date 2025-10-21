from fastapi import APIRouter, HTTPException
from models.schemas import QuestionRequest, QuestionResponse, MCQItem, MCQOption
from core.gemini_client import get_model
from models.utils import safe_json_parse, gen_id
import random

router = APIRouter(prefix="/generate", tags=["generate"])

PROMPT_TEMPLATE = """
You are an AI-based question generator for assessing high school students' {track} readiness.
Generate {count} multiple-choice questions across EASY, MEDIUM, and HARD difficulties 
to simulate adaptive testing. Each question must have:
- id (string)
- question (clear and concise)
- 4 options (A, B, C, D)
- correct answer key (A|B|C|D)
- competency_domain (logic, creativity, interpersonal, practical, or strategy)
- level (easy, medium, or hard)

Return STRICT JSON ONLY, in this exact structure:
{{
  "items": [
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
      "level": "easy|medium|hard"
    }}
  ]
}}

Rules:
- Output pure JSON (no commentary, no markdown, no explanation).
- Questions should mix cognitive and situational reasoning relevant to the chosen track.
- Maintain balance across domains.
"""

@router.post("", response_model=QuestionResponse)
async def generate_questions(req: QuestionRequest):
    """
    Generate a batch of adaptive questions (10–25 items) with mixed difficulty.
    The Gemini model is instructed to output strict JSON structure.
    """
    model = get_model()

    # Enforce adaptive batch if count >= 10
    if req.count >= 10:
        # Randomized adaptive distribution
        level_mix = random.choices(
            ["easy", "medium", "hard"], 
            weights=[0.3, 0.4, 0.3], 
            k=req.count
        )
        prompt = PROMPT_TEMPLATE.format(track=req.track, count=req.count)
    else:
        # fallback to uniform difficulty
        level_mix = [req.level] * req.count
        prompt = PROMPT_TEMPLATE.format(track=req.track, count=req.count)

    res = model.generate_content(prompt)
    raw_text = res.text.strip()

    # Sanitize & Parse JSON
    data = safe_json_parse(raw_text, {"items": []})

    # fallback manual cleanup if JSON is malformed
    if isinstance(data, str):
        data = safe_json_parse(data, {"items": []})
    if not isinstance(data, dict):
        data = {"items": []}

    items = []
    for i, it in enumerate(data.get("items", [])):
        try:
            items.append(
                MCQItem(
                    id=it.get("id") or gen_id(),
                    question=it.get("question", f"Question {i+1}?"),
                    options=[MCQOption(**opt) for opt in it.get("options", [])],
                    answer=it.get("answer", random.choice(["A", "B", "C", "D"])),
                    competency_domain=it.get(
                        "competency_domain", random.choice(
                            ["logic", "creativity", "interpersonal", "practical", "strategy"]
                        )
                    ),
                    level=it.get("level", level_mix[i % len(level_mix)]),
                )
            )
        except Exception as e:
            print(f"⚠️ Skipped invalid item {i}: {e}")
            continue

    if not items:
        raise HTTPException(500, "Failed to generate valid items")

    # ✅ Final safeguard: limit to requested count & randomize order
    random.shuffle(items)
    return QuestionResponse(items=items[:req.count])
