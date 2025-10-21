from fastapi import APIRouter
from models.schemas import VoiceRequest, VoiceEvalResponse
from core.gemini_client import get_model
from models.utils import safe_json_parse

router = APIRouter(prefix="/voice", tags=["voice"])

@router.post("/evaluate", response_model=VoiceEvalResponse)
async def voice_evaluation(req: VoiceRequest):
    model = get_model()

    # gunakan f-string agar JSON tidak bentrok dengan {}
    PROMPT = f"""
You are an AI evaluator analyzing a student's voice reflection.
Evaluate the following transcript and respond in STRICT JSON format:

{{
  "confidence": number (0-100),
  "positivity": number (0-100),
  "empathy": number (0-100),
  "summary": "a concise paragraph summarizing tone, clarity, and coherence"
}}

Transcript:
{req.transcript}
"""

    # kirim prompt ke Gemini
    res = model.generate_content(PROMPT)

    # parse hasil LLM
    data = safe_json_parse(res.text, {})

    # fallback jika parsing gagal atau field kosong
    return VoiceEvalResponse(
        confidence=int(data.get("confidence", 60)),
        positivity=int(data.get("positivity", 60)),
        empathy=int(data.get("empathy", 60)),
        summary=data.get(
            "summary",
            "Initial evaluation based on provided transcript."
        ),
    )
