from fastapi import APIRouter
from models.schemas import BehaviorRequest, BehaviorResponse

router = APIRouter(prefix="/behavior", tags=["behavior"])

@router.post("/analyze", response_model=BehaviorResponse)
async def behavioral_analysis(req: BehaviorRequest):
    # Simple heuristics for MVP
    avg_time = sum(req.response_times)/len(req.response_times) if req.response_times else 0.0
    attention = max(0, min(100, int(100 - (avg_time * 10) - (req.interruptions * 5))))
    processing = max(0, min(100, int(100 - (avg_time * 15))))
    consistency = max(0, min(100, req.consistency_score))
    return BehaviorResponse(
        attention_score=attention,
        processing_speed=processing,
        consistency=consistency
    )
