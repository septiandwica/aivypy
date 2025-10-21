from fastapi import APIRouter
from models.schemas import ProfileRequest, CareerMatchResponse

router = APIRouter(prefix="/career", tags=["career"])

@router.post("/match", response_model=CareerMatchResponse)
async def career_match(req: ProfileRequest):
    # Simple rule-based mapping for MVP
    if req.logic >= 80 and req.strategy >= 70:
        return CareerMatchResponse(
            major="Computer Science",
            career="Data Analyst",
            rationale="High logical reasoning and strategic thinking align with analytics roles."
        )
    if req.interpersonal >= 80:
        return CareerMatchResponse(
            major="Psychology/Business",
            career="HR Specialist",
            rationale="Strong interpersonal skills support people-oriented careers."
        )
    if req.creativity >= 80 and req.practical >= 60:
        return CareerMatchResponse(
            major="Design/Communication",
            career="UX Designer",
            rationale="Creative and practical balance fits user-centered design."
        )
    return CareerMatchResponse(
        major="Business Administration",
        career="Marketing Associate",
        rationale="Balanced profile suits generalist roles with growth potential."
    )
