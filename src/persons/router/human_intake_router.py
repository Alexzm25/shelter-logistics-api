from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.persons.schemas.human_intake_schemas import (
    DashboardResponse,
    EvaluateCandidateRequest,
    EvaluationResponse,
    ProfessionOptionResponse,
    RegisterCandidateRequest,
    RegisterCandidateResponse,
)
from src.persons.service.human_intake_service import HumanIntakeService


router = APIRouter(prefix="/human", tags=["Human Intake"])


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(
    camp_id: int = Query(default=1, ge=1),
    db: Session = Depends(get_db),
) -> DashboardResponse:
    return HumanIntakeService.get_dashboard(db, camp_id)


@router.get("/professions", response_model=list[ProfessionOptionResponse])
def get_professions(db: Session = Depends(get_db)) -> list[ProfessionOptionResponse]:
    return HumanIntakeService.get_professions(db)


@router.post("/evaluate", response_model=EvaluationResponse)
def evaluate_candidate(
    payload: EvaluateCandidateRequest,
    db: Session = Depends(get_db),
) -> EvaluationResponse:
    return HumanIntakeService.evaluate_candidate(db, payload.candidate)


@router.post("/register", response_model=RegisterCandidateResponse)
def register_candidate(
    payload: RegisterCandidateRequest,
    db: Session = Depends(get_db),
) -> RegisterCandidateResponse:
    return HumanIntakeService.register_candidate(db, payload)
