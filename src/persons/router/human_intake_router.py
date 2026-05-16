from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.auth.schemas.user_profile import UserProfileResponse
from src.auth.service.authorization import (
    PERM_HEAL,
    PERM_HUMAN_FULL,
    ROLE_ADMIN,
    ROLE_WORKER,
    enforce_role_permissions,
    get_current_user_from_token,
)
from src.core.database import get_db
from src.persons.schemas.human_intake_schemas import (
    DashboardResponse,
    EvaluateCandidateRequest,
    EvaluationResponse,
    PersonSummaryResponse,
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
    current_user: UserProfileResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
) -> DashboardResponse:
    if current_user.role_name == ROLE_ADMIN:
        enforce_role_permissions(db, current_user, {ROLE_ADMIN}, {PERM_HUMAN_FULL})
    elif current_user.role_name == ROLE_WORKER:
        enforce_role_permissions(db, current_user, {ROLE_WORKER}, {PERM_HEAL})
        profession_name = (current_user.profession_name or "").upper()
        if profession_name != "MEDICO":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Profesion no autorizada",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Rol no autorizado",
        )

    return HumanIntakeService.get_dashboard(db, camp_id)


@router.get("/professions", response_model=list[ProfessionOptionResponse])
def get_professions(
    current_user: UserProfileResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
) -> list[ProfessionOptionResponse]:
    enforce_role_permissions(db, current_user, {ROLE_ADMIN}, {PERM_HUMAN_FULL})
    return HumanIntakeService.get_professions(db)


@router.get("/people/available-for-profession/{profession_name}", response_model=list[PersonSummaryResponse])
def get_available_people_for_profession(
    profession_name: str,
    camp_id: int = Query(default=1, ge=1),
    current_user: UserProfileResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
) -> list[PersonSummaryResponse]:
    enforce_role_permissions(db, current_user, {ROLE_ADMIN}, {PERM_HUMAN_FULL})
    return HumanIntakeService.get_available_people_for_profession(db, profession_name, camp_id)


@router.get("/people/by-id-card/{id_card}", response_model=PersonSummaryResponse)
def get_person_by_id_card(
    id_card: str,
    camp_id: int = Query(default=1, ge=1),
    current_user: UserProfileResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
) -> PersonSummaryResponse:
    enforce_role_permissions(db, current_user, {ROLE_ADMIN}, {PERM_HUMAN_FULL})
    return HumanIntakeService.find_person_by_id_card(db, id_card, camp_id)


@router.post("/evaluate", response_model=EvaluationResponse)
def evaluate_candidate(
    payload: EvaluateCandidateRequest,
    current_user: UserProfileResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
) -> EvaluationResponse:
    enforce_role_permissions(db, current_user, {ROLE_ADMIN}, {PERM_HUMAN_FULL})
    return HumanIntakeService.evaluate_candidate(db, payload.candidate)


@router.post("/register", response_model=RegisterCandidateResponse)
def register_candidate(
    payload: RegisterCandidateRequest,
    current_user: UserProfileResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
) -> RegisterCandidateResponse:
    enforce_role_permissions(db, current_user, {ROLE_ADMIN}, {PERM_HUMAN_FULL})
    return HumanIntakeService.register_candidate(db, payload)


@router.patch("/people/{person_id}", response_model=UpdatePersonResponse)
def update_person(
    person_id: int,
    payload: UpdatePersonRequest,
    current_user: UserProfileResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
) -> UpdatePersonResponse:
    enforce_role_permissions(db, current_user, {ROLE_ADMIN}, {PERM_HUMAN_FULL})
    return HumanIntakeService.update_person(db, person_id, payload)


@router.patch("/people/{person_id}/status", response_model=UpdatePersonStatusResponse)
def update_person_status(
    person_id: int,
    payload: UpdatePersonStatusRequest,
    current_user: UserProfileResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
) -> UpdatePersonStatusResponse:
    if current_user.role_name == ROLE_ADMIN:
        enforce_role_permissions(db, current_user, {ROLE_ADMIN}, {PERM_HUMAN_FULL})
    elif current_user.role_name == ROLE_WORKER:
        enforce_role_permissions(db, current_user, {ROLE_WORKER}, {PERM_HEAL})
        profession_name = (current_user.profession_name or "").upper()
        if profession_name != "MEDICO":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Profesion no autorizada",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Rol no autorizado",
        )

    return HumanIntakeService.update_person_status(db, person_id, payload)


@router.post("/people/{person_id}/temporary-reassignment", response_model=TemporaryReassignmentResponse)
def create_temporary_reassignment(
    person_id: int,
    payload: TemporaryReassignmentRequest,
    current_user: UserProfileResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
) -> TemporaryReassignmentResponse:
    enforce_role_permissions(db, current_user, {ROLE_ADMIN}, {PERM_HUMAN_FULL})
    return HumanIntakeService.create_temporary_reassignment(db, person_id, payload)


@router.delete("/people/{person_id}/temporary-reassignment", response_model=TemporaryReassignmentResponse)
def close_temporary_reassignment(
    person_id: int,
    current_user: UserProfileResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
) -> TemporaryReassignmentResponse:
    enforce_role_permissions(db, current_user, {ROLE_ADMIN}, {PERM_HUMAN_FULL})
    return HumanIntakeService.close_temporary_reassignment(db, person_id)
