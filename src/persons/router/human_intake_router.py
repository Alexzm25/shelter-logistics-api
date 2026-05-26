from typing import Literal

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
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
from src.core.cloudinary import upload_image_to_cloudinary
from src.persons.schemas.human_intake_schemas import (
    CandidateInput,
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

    return HumanIntakeService.get_dashboard(db, current_user.camp_id)


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
    current_user: UserProfileResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
) -> list[PersonSummaryResponse]:
    enforce_role_permissions(db, current_user, {ROLE_ADMIN}, {PERM_HUMAN_FULL})
    return HumanIntakeService.get_available_people_for_profession(db, profession_name, current_user.camp_id)


@router.get("/people/by-id-card/{id_card}", response_model=PersonSummaryResponse)
def get_person_by_id_card(
    id_card: str,
    current_user: UserProfileResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
) -> PersonSummaryResponse:
    enforce_role_permissions(db, current_user, {ROLE_ADMIN}, {PERM_HUMAN_FULL})
    return HumanIntakeService.find_person_by_id_card(db, id_card, current_user.camp_id)


@router.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_candidate(
    payload: EvaluateCandidateRequest,
    current_user: UserProfileResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
) -> EvaluationResponse:
    enforce_role_permissions(db, current_user, {ROLE_ADMIN}, {PERM_HUMAN_FULL})
    return await HumanIntakeService.evaluate_candidate(db, payload.candidate)


@router.post("/register", response_model=RegisterCandidateResponse)
async def register_candidate(
    first_name: str = Form(...),
    last_name: str = Form(...),
    age: int = Form(..., ge=0, le=120),
    background_info: str = Form(...),
    weight: float = Form(..., ge=0),
    height: float = Form(..., ge=0),
    camp_id: int = Form(..., ge=1),
    human_decision: Literal["PERMITIR_INGRESO", "RECHAZAR_INGRESO"] = Form(...),
    password: str = Form(...),
    username: str | None = Form(None),
    selected_profession: str | None = Form(None),
    id_card: str | None = Form(None),
    photo_url: str | None = Form(None),
    photo_file: UploadFile | None = File(None),
    current_user: UserProfileResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
) -> RegisterCandidateResponse:
    enforce_role_permissions(db, current_user, {ROLE_ADMIN}, {PERM_HUMAN_FULL})

    resolved_photo_url = (photo_url or "").strip() or None
    if photo_file is not None:
        content_type = (photo_file.content_type or "").lower()
        if not content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Solo se permiten archivos de imagen.",
            )
        resolved_photo_url = upload_image_to_cloudinary(photo_file, folder="/persons")

    payload = RegisterCandidateRequest(
        candidate=CandidateInput(
            first_name=first_name,
            last_name=last_name,
            age=age,
            background_info=background_info,
            weight=weight,
            height=height,
            id_card=(id_card or "").strip() or None,
            photo_url=resolved_photo_url,
            camp_id=camp_id,
        ),
        human_decision=human_decision,
        password=password,
        username=(username or "").strip() or None,
        selected_profession=(selected_profession or "").strip() or None,
    )
    return await HumanIntakeService.register_candidate(db, payload)


@router.patch("/people/{person_id}", response_model=UpdatePersonResponse)
def update_person(
    person_id: int,
    first_name: str = Form(...),
    last_name: str = Form(...),
    age: int = Form(..., ge=0, le=120),
    background_info: str = Form(...),
    weight: float = Form(..., ge=0),
    height: float = Form(..., ge=0),
    id_card: str | None = Form(None),
    photo_url: str | None = Form(None),
    photo_file: UploadFile | None = File(None),
    current_user: UserProfileResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
) -> UpdatePersonResponse:
    enforce_role_permissions(db, current_user, {ROLE_ADMIN}, {PERM_HUMAN_FULL})

    resolved_photo_url = (photo_url or "").strip() or None
    if photo_file is not None:
        content_type = (photo_file.content_type or "").lower()
        if not content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Solo se permiten archivos de imagen.",
            )
        resolved_photo_url = upload_image_to_cloudinary(photo_file, folder="/persons")

    payload = UpdatePersonRequest(
        first_name=first_name,
        last_name=last_name,
        age=age,
        background_info=background_info,
        weight=weight,
        height=height,
        id_card=(id_card or "").strip() or None,
        photo_url=resolved_photo_url,
    )
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
