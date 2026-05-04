from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.persons.schemas.human_intake_schemas import (
    DashboardResponse,
    EvaluateCandidateRequest,
    EvaluationResponse,
    ProfessionOptionResponse,
    TemporaryReassignmentRequest,
    TemporaryReassignmentResponse,
    UpdatePersonRequest,
    UpdatePersonResponse,
    UpdatePersonStatusRequest,
    UpdatePersonStatusResponse,
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


@router.patch("/people/{person_id}", response_model=UpdatePersonResponse)
def update_person(
    person_id: int,
    payload: UpdatePersonRequest,
    db: Session = Depends(get_db),
) -> UpdatePersonResponse:
    return HumanIntakeService.update_person(db, person_id, payload)


@router.patch("/people/{person_id}/status", response_model=UpdatePersonStatusResponse)
def update_person_status(
    person_id: int,
    payload: UpdatePersonStatusRequest,
    db: Session = Depends(get_db),
) -> UpdatePersonStatusResponse:
    return HumanIntakeService.update_person_status(db, person_id, payload)


@router.post("/people/{person_id}/temporary-reassignment", response_model=TemporaryReassignmentResponse)
def create_temporary_reassignment(
    person_id: int,
    payload: TemporaryReassignmentRequest,
    db: Session = Depends(get_db),
) -> TemporaryReassignmentResponse:
    return HumanIntakeService.create_temporary_reassignment(db, person_id, payload)


@router.delete("/people/{person_id}/temporary-reassignment", response_model=TemporaryReassignmentResponse)
def close_temporary_reassignment(
    person_id: int,
    db: Session = Depends(get_db),
) -> TemporaryReassignmentResponse:
    return HumanIntakeService.close_temporary_reassignment(db, person_id)
