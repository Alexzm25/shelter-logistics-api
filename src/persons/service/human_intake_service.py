from datetime import date, datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.ai.enums.ai_decision_enum import AIDecisionEnum
from src.ai.models.ai_configuration import AIConfiguration
from src.ai.models.ai_log import AILog
from src.ai.service.groq_evaluation_service import GroqEvaluationService
from src.auth.models import AppUser, Role
from src.auth.service.authorization import ROLE_WORKER
from src.auth.service.security import create_password_hash
from src.camps.models.camp import Camp  # noqa: F401
from src.persons.enums.current_status_enum import CurrentStatusEnum
from src.persons.enums.health_status_enum import HealthStatusEnum
from src.persons.enums.health_work_restrictions import (
    can_work,
    is_valid_health_transition,
)
from src.persons.models.person import Person
from src.persons.models.profession import Profession
from src.persons.models.profession_assignment import ProfessionAssignment
from src.persons.schemas.human_intake_schemas import (
    AILogSummaryResponse,
    CandidateInput,
    DashboardResponse,
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
    ScoreBreakdownResponse,
)


class HumanIntakeService:
    ROLE_DB_NAMES = {
        "MEDIC": "MEDICO",
        "EXPLORER": "EXPLORADOR",
        "FARMER": "AGRICULTOR",
    }
    TRACKED_ROLES = ("MEDIC", "EXPLORER", "FARMER")

    @staticmethod
    async def evaluate_candidate(db: Session, candidate: CandidateInput) -> EvaluationResponse:
        role_counts = HumanIntakeService._get_role_counts(db, candidate.camp_id)
        active_config = (
            db.query(AIConfiguration)
            .filter(AIConfiguration.is_active.is_(True))
            .order_by(AIConfiguration.id.desc())
            .first()
        )
        evaluation = await GroqEvaluationService.evaluate_candidate(
            candidate,
            role_counts,
            config_prompt=active_config.prompt if active_config else None,
            config_rules=active_config.rules if active_config else None,
        )
        return EvaluationResponse(
            decision=HumanIntakeService._normalize_ai_decision(evaluation.decision),
            score=evaluation.score,
            explanation=evaluation.explanation,
            suggested_profession=HumanIntakeService._ai_role_to_db_role(evaluation.suggested_profession),
            score_breakdown=evaluation.score_breakdown,
            applied_rules=evaluation.applied_rules,
            config_name=active_config.name if active_config else None,
        )

    @staticmethod
    def get_professions(db: Session) -> list[ProfessionOptionResponse]:
        profession_rows = db.query(Profession.name, Profession.is_critical).order_by(Profession.name.asc()).all()
        return [ProfessionOptionResponse(name=name, is_critical=is_critical) for name, is_critical in profession_rows]

    @staticmethod
    async def register_candidate(db: Session, payload: RegisterCandidateRequest) -> RegisterCandidateResponse:
        evaluation = await HumanIntakeService.evaluate_candidate(db, payload.candidate)
        allow_entry = payload.human_decision == "PERMITIR_INGRESO"
        selected_profession = (payload.selected_profession or "").strip()
        candidate_id_card = (payload.candidate.id_card or "AUTO-GENERATED").strip()

        if allow_entry and not selected_profession:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="A profession must be selected before registration.",
            )

        created_person = (
            db.query(Person)
            .filter(
                Person.id_card == candidate_id_card,
                Person.camp_id == payload.candidate.camp_id,
            )
            .order_by(Person.id.desc())
            .first()
        )

        if created_person and created_person.is_active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Esta persona ya se encuentra activa en el campamento.",
            )

        if created_person is None:
            candidate_age = HumanIntakeService._compute_age(payload.candidate.birth_date)
            created_person = Person(
                name=payload.candidate.first_name.strip(),
                last_name=payload.candidate.last_name.strip(),
                age=candidate_age,
                background_info=payload.candidate.background_info.strip(),
                weight=payload.candidate.weight,
                height=payload.candidate.height,
                camp_id=payload.candidate.camp_id,
                current_status=(
                    CurrentStatusEnum.TRABAJANDO if allow_entry else CurrentStatusEnum.LIBRE
                ),
                health_status=HumanIntakeService._infer_health_status(payload.candidate.background_info),
                camp_entry_date=datetime.now(timezone.utc),
                photo_url=(payload.candidate.photo_url or "").strip(),
                is_active=allow_entry,
                id_card=candidate_id_card,
            )
            db.add(created_person)
            db.flush()
        else:
            HumanIntakeService._deactivate_all_active_profession_assignments(db, created_person.id)
            created_person.name = payload.candidate.first_name.strip()
            created_person.last_name = payload.candidate.last_name.strip()
            created_person.age = HumanIntakeService._compute_age(payload.candidate.birth_date)
            created_person.background_info = payload.candidate.background_info.strip()
            created_person.weight = payload.candidate.weight
            created_person.height = payload.candidate.height
            created_person.camp_id = payload.candidate.camp_id
            created_person.health_status = HumanIntakeService._infer_health_status(payload.candidate.background_info)
            created_person.camp_entry_date = datetime.now(timezone.utc)
            created_person.photo_url = (payload.candidate.photo_url or "").strip()
            created_person.is_active = allow_entry
            created_person.current_status = (
                CurrentStatusEnum.TRABAJANDO if created_person.is_active else CurrentStatusEnum.LIBRE
            )
            created_person.id_card = candidate_id_card

        if allow_entry:
            assigned = HumanIntakeService._create_profession_assignment(
                db=db,
                person_id=created_person.id,
                role_name=selected_profession,
            )
            if not assigned:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Selected profession '{selected_profession}' does not exist.",
                )

            HumanIntakeService._upsert_worker_user(db, created_person, payload.password, payload.username)

        created_log = AILog(
            decision_reason=evaluation.explanation,
            ai_decision=(
                AIDecisionEnum.APROBADO if evaluation.decision == "APROBADO" else AIDecisionEnum.RECHAZADO
            ),
            evaluation_context={
                "first_name": payload.candidate.first_name,
                "last_name": payload.candidate.last_name,
                "background_info": payload.candidate.background_info,
                "score": evaluation.score,
                "suggested_profession": evaluation.suggested_profession,
                "selected_profession": selected_profession or evaluation.suggested_profession,
                "score_breakdown": evaluation.score_breakdown.model_dump(),
                "applied_rules": evaluation.applied_rules,
            },
            camp_id=payload.candidate.camp_id,
            person_id=created_person.id,
            final_user_decision=allow_entry,
        )
        db.add(created_log)

        db.commit()
        db.refresh(created_log)
        if created_person:
            db.refresh(created_person)

        return RegisterCandidateResponse(
            evaluation=evaluation,
            created_person=HumanIntakeService._to_person_summary(db, created_person),
            created_ai_log=HumanIntakeService._to_ai_log_summary(created_log),
            message=(
                "Persona registrada correctamente"
                if allow_entry
                else "Persona guardada correctamente, pero el ingreso fue rechazado"
            ),
        )

    @staticmethod
    def find_person_by_id_card(db: Session, id_card: str, camp_id: int) -> PersonSummaryResponse:
        normalized_id_card = id_card.strip()
        if not normalized_id_card:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Id card is required.",
            )

        people = (
            db.query(Person)
            .filter(Person.id_card == normalized_id_card)
            .order_by(Person.id.desc())
            .all()
        )

        if not people:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Person with id card '{normalized_id_card}' not found.",
            )

        active_same_camp_person = next(
            (person for person in people if person.camp_id == camp_id and person.is_active),
            None,
        )
        if active_same_camp_person:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Esta persona ya se encuentra activa en el campamento.",
            )

        same_camp_person = next((person for person in people if person.camp_id == camp_id), None)
        candidate_person = same_camp_person or people[0]
        return HumanIntakeService._to_person_summary(db, candidate_person)

    @staticmethod
    def get_dashboard(db: Session, camp_id: int) -> DashboardResponse:
        people = (
            db.query(Person)
            .filter(Person.camp_id == camp_id, Person.is_active.is_(True))
            .order_by(Person.id.desc())
            .all()
        )
        logs = db.query(AILog).filter(AILog.camp_id == camp_id).order_by(AILog.id.desc()).all()

        person_ids = [p.id for p in people]

        # Batch pre-fetch main profession assignments
        profession_rows = (
            db.query(ProfessionAssignment.person_id, Profession.name)
            .join(Profession, ProfessionAssignment.profession_id == Profession.id)
            .filter(
                ProfessionAssignment.person_id.in_(person_ids),
                ProfessionAssignment.is_active.is_(True),
                ProfessionAssignment.is_main_profession.is_(True),
            )
            .all()
        )
        profession_by_person: dict[int, str] = {row.person_id: row.name for row in profession_rows}

        # Batch pre-fetch temporary reassignments
        reassignment_rows = (
            db.query(ProfessionAssignment.person_id, Profession.name)
            .join(Profession, ProfessionAssignment.profession_id == Profession.id)
            .filter(
                ProfessionAssignment.person_id.in_(person_ids),
                ProfessionAssignment.is_active.is_(True),
                ProfessionAssignment.is_main_profession.is_(False),
            )
            .order_by(ProfessionAssignment.person_id, ProfessionAssignment.id.desc())
            .all()
        )
        reassignment_by_person: dict[int, str] = {}
        for row in reassignment_rows:
            reassignment_by_person[row.person_id] = row.name

        people_response = [
            HumanIntakeService._to_person_summary_batched(db, person, profession_by_person, reassignment_by_person)
            for person in people
        ]
        logs_response = [HumanIntakeService._to_ai_log_summary(log) for log in logs]

        return DashboardResponse(people=people_response, ai_logs=logs_response)

    @staticmethod
    def get_available_people_for_profession(db: Session, profession_name: str, camp_id: int) -> list[PersonSummaryResponse]:
        normalized_profession = profession_name.strip()
        if not normalized_profession:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Profession name is required.",
            )

        profession = db.query(Profession).filter(Profession.name == normalized_profession).first()
        if not profession:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profession '{normalized_profession}' not found.",
            )

        people = (
            db.query(Person)
            .join(ProfessionAssignment, ProfessionAssignment.person_id == Person.id)
            .filter(
                Person.camp_id == camp_id,
                Person.is_active.is_(True),
                Person.health_status == HealthStatusEnum.SANO,
                Person.current_status == CurrentStatusEnum.LIBRE,
                ProfessionAssignment.profession_id == profession.id,
                ProfessionAssignment.is_main_profession.is_(True),
                ProfessionAssignment.is_active.is_(True),
            )
            .order_by(Person.id.asc())
            .all()
        )

        return [HumanIntakeService._to_person_summary(db, person) for person in people]

    @staticmethod
    def update_person(db: Session, person_id: int, payload: UpdatePersonRequest) -> UpdatePersonResponse:
        person = db.query(Person).filter(Person.id == person_id).first()
        if not person:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Person {person_id} not found.",
            )

        person.name = payload.first_name.strip()
        person.last_name = payload.last_name.strip()
        person.age = HumanIntakeService._compute_age(payload.birth_date)
        person.background_info = payload.background_info.strip()
        person.weight = payload.weight
        person.height = payload.height
        person.id_card = (payload.id_card or "").strip() or person.id_card
        person.photo_url = (payload.photo_url or "").strip()
        person.health_status = HumanIntakeService._infer_health_status(payload.background_info)

        db.commit()
        db.refresh(person)

        return UpdatePersonResponse(
            person=HumanIntakeService._to_person_summary(db, person),
            message="Persona editada correctamente"
        )

    @staticmethod
    def update_person_status(
        db: Session,
        person_id: int,
        payload: UpdatePersonStatusRequest,
    ) -> UpdatePersonStatusResponse:
        person = db.query(Person).filter(Person.id == person_id).first()
        if not person:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Person {person_id} not found.",
            )

        if payload.health_status is None and payload.current_status is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="At least one status field must be provided.",
            )

        previous_health_status = person.health_status.value
        next_health_status = payload.health_status or previous_health_status

        is_transition_valid, transition_message = is_valid_health_transition(previous_health_status, next_health_status)
        if not is_transition_valid:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=transition_message,
            )

        if not can_work(next_health_status):
            if payload.current_status is not None and payload.current_status != CurrentStatusEnum.LIBRE.value:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Person with health status '{next_health_status}' cannot have working current_status.",
                )

        if payload.health_status is not None:
            person.health_status = HealthStatusEnum(payload.health_status)

        if payload.current_status is not None and can_work(next_health_status):
            person.current_status = CurrentStatusEnum(payload.current_status)

        db.commit()
        db.refresh(person)

        return UpdatePersonStatusResponse(
            person=HumanIntakeService._to_person_summary(db, person),
            message="Estado de persona actualizado correctamente",
        )

    @staticmethod
    def create_temporary_reassignment(
        db: Session,
        person_id: int,
        payload: TemporaryReassignmentRequest,
    ) -> TemporaryReassignmentResponse:
        person = db.query(Person).filter(Person.id == person_id).first()
        if not person:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Person {person_id} not found.",
            )

        if person.health_status != HealthStatusEnum.SANO:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Only people with SANO health status can be temporarily reassigned.",
            )

        profession = db.query(Profession).filter(Profession.name == payload.profession_name.strip()).first()
        if not profession:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profession '{payload.profession_name}' not found.",
            )

        current_profession_name = HumanIntakeService._resolve_profession_for_person(db, person.id)
        if not current_profession_name:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Person must have an active main profession before being reassigned.",
            )

        available_workers = HumanIntakeService._count_available_workers_for_profession(
            db,
            person.camp_id,
            current_profession_name,
        )
        if available_workers <= 1:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    f"Al realizar este movimiento, {current_profession_name} quedará en estado crítico "
                    "porque no tendrá trabajadores disponibles."
                ),
            )

        # Close any existing active temporary reassignment before creating a new one
        active_temporary_assignment = (
            db.query(ProfessionAssignment)
            .filter(
                ProfessionAssignment.person_id == person_id,
                ProfessionAssignment.is_active.is_(True),
                ProfessionAssignment.is_main_profession.is_(False),
            )
            .order_by(ProfessionAssignment.id.desc())
            .first()
        )

        if active_temporary_assignment:
            active_temporary_assignment.is_active = False
            active_temporary_assignment.end_date = date.today()

        # Create new temporary reassignment
        new_temporary_assignment = ProfessionAssignment(
            start_date=date.today(),
            end_date=None,
            reason=payload.reason,
            is_main_profession=False,
            profession_id=profession.id,
            person_id=person_id,
            is_active=True,
        )
        db.add(new_temporary_assignment)
        db.commit()
        db.refresh(person)

        return TemporaryReassignmentResponse(
            person=HumanIntakeService._to_person_summary(db, person),
            message="Reasignación temporal creada correctamente",
        )

    @staticmethod
    def close_temporary_reassignment(
        db: Session,
        person_id: int,
    ) -> TemporaryReassignmentResponse:
        person = db.query(Person).filter(Person.id == person_id).first()
        if not person:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Person {person_id} not found.",
            )

        active_temporary_assignment = (
            db.query(ProfessionAssignment)
            .filter(
                ProfessionAssignment.person_id == person_id,
                ProfessionAssignment.is_active.is_(True),
                ProfessionAssignment.is_main_profession.is_(False),
            )
            .order_by(ProfessionAssignment.id.desc())
            .first()
        )

        if not active_temporary_assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active temporary reassignment found.",
            )

        active_temporary_assignment.is_active = False
        active_temporary_assignment.end_date = date.today()
        db.commit()
        db.refresh(person)

        return TemporaryReassignmentResponse(
            person=HumanIntakeService._to_person_summary(db, person),
            message="Reasignación temporal cerrada correctamente",
        )

    @staticmethod
    def _infer_health_status(background_info: str) -> HealthStatusEnum:
        normalized = background_info.lower()
        if any(token in normalized for token in ("dead", "deceased")):
            return HealthStatusEnum.MUERTO
        if any(token in normalized for token in ("sick", "fever", "infection", "cough", "symptom")):
            return HealthStatusEnum.ENFERMO
        if any(token in normalized for token in ("injur", "fractur", "bleed", "lesion")):
            return HealthStatusEnum.HERIDO
        return HealthStatusEnum.SANO

    @staticmethod
    def _compute_age(birth_date: date) -> int:
        today = date.today()
        years = today.year - birth_date.year
        if (today.month, today.day) < (birth_date.month, birth_date.day):
            years -= 1
        return max(0, years)

    @staticmethod
    def _to_api_health_status(db_status: HealthStatusEnum) -> str:
        return db_status.value

    @staticmethod
    def _get_role_counts(db: Session, camp_id: int) -> dict[str, int]:
        role_counts = {role: 0 for role in HumanIntakeService.TRACKED_ROLES}

        assignments = (
            db.query(Profession.name)
            .join(ProfessionAssignment, ProfessionAssignment.profession_id == Profession.id)
            .join(Person, Person.id == ProfessionAssignment.person_id)
            .filter(
                Person.camp_id == camp_id,
                ProfessionAssignment.is_active.is_(True),
                ProfessionAssignment.is_main_profession.is_(True),
            )
            .all()
        )

        for assignment in assignments:
            db_role_name = assignment[0]
            role_name = HumanIntakeService._db_role_to_api_role(db_role_name)
            if role_name:
                role_counts[role_name] += 1

        return role_counts

    @staticmethod
    def _count_available_workers_for_profession(db: Session, camp_id: int, profession_name: str) -> int:
        active_people = (
            db.query(Person.id)
            .filter(
                Person.camp_id == camp_id,
                Person.is_active.is_(True),
                Person.health_status == HealthStatusEnum.SANO,
                Person.current_status == CurrentStatusEnum.LIBRE,
            )
            .all()
        )

        person_ids = [row.id for row in active_people]
        if not person_ids:
            return 0

        profession_rows = (
            db.query(ProfessionAssignment.person_id, Profession.name)
            .join(Profession, ProfessionAssignment.profession_id == Profession.id)
            .filter(
                ProfessionAssignment.person_id.in_(person_ids),
                ProfessionAssignment.is_active.is_(True),
                ProfessionAssignment.is_main_profession.is_(True),
            )
            .all()
        )
        profession_by_person: dict[int, str] = {row.person_id: row.name for row in profession_rows}

        reassignment_rows = (
            db.query(ProfessionAssignment.person_id, Profession.name)
            .join(Profession, ProfessionAssignment.profession_id == Profession.id)
            .filter(
                ProfessionAssignment.person_id.in_(person_ids),
                ProfessionAssignment.is_active.is_(True),
                ProfessionAssignment.is_main_profession.is_(False),
            )
            .order_by(ProfessionAssignment.person_id, ProfessionAssignment.id.desc())
            .all()
        )
        reassignment_by_person: dict[int, str] = {}
        for row in reassignment_rows:
            reassignment_by_person[row.person_id] = row.name

        return sum(
            1
            for person_id in person_ids
            if (reassignment_by_person.get(person_id) or profession_by_person.get(person_id)) == profession_name
        )

    @staticmethod
    def _create_profession_assignment(db: Session, person_id: int, role_name: str) -> bool:
        normalized = role_name.strip()
        if not normalized:
            return False

        db_role_name = HumanIntakeService.ROLE_DB_NAMES.get(normalized, normalized)

        profession = db.query(Profession).filter(Profession.name == db_role_name).first()
        if not profession:
            return False

        assignment = ProfessionAssignment(
            start_date=date.today(),
            end_date=None,
            reason="Auto-assigned by intake workflow",
            is_main_profession=True,
            profession_id=profession.id,
            person_id=person_id,
            is_active=True,
        )
        db.add(assignment)
        return True

    @staticmethod
    def _upsert_worker_user(db: Session, person: Person, password: str, requested_username: str | None = None) -> None:
        normalized_password = password.strip()
        if not normalized_password:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Password is required before registration.",
            )

        role = db.query(Role).filter(Role.name == ROLE_WORKER).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Worker role not found.",
            )

        if requested_username:
            username = requested_username.strip()
        else:
            username = HumanIntakeService._build_worker_username(db, person)
        password_hash = create_password_hash(normalized_password)
        existing_user = db.query(AppUser).filter(AppUser.person_id == person.id).first()

        if existing_user:
            existing_user.username = username
            existing_user.password_hash = password_hash
            existing_user.role_id = role.id
            return

        db.add(
            AppUser(
                username=username,
                password_hash=password_hash,
                person_id=person.id,
                role_id=role.id,
            )
        )

    @staticmethod
    def _build_worker_username(db: Session, person: Person) -> str:
        base_username = "".join(character for character in person.name.lower().strip() if character.isalnum())
        if not base_username:
            base_username = f"trabajador{person.id}"

        username = base_username[:20]
        username_conflict = (
            db.query(AppUser)
            .filter(AppUser.username == username, AppUser.person_id != person.id)
            .first()
        )

        if not username_conflict:
            return username

        suffix = f"-{person.id}"
        max_base_length = max(1, 20 - len(suffix))
        return f"{base_username[:max_base_length]}{suffix}"

    @staticmethod
    def _deactivate_all_active_profession_assignments(db: Session, person_id: int) -> None:
        assignments = (
            db.query(ProfessionAssignment)
            .filter(
                ProfessionAssignment.person_id == person_id,
                ProfessionAssignment.is_active.is_(True),
            )
            .all()
        )
        for assignment in assignments:
            assignment.is_active = False
            assignment.end_date = date.today()

    @staticmethod
    def _restore_last_main_profession_assignment(db: Session, person_id: int) -> bool:
        assignment = (
            db.query(ProfessionAssignment)
            .filter(
                ProfessionAssignment.person_id == person_id,
                ProfessionAssignment.is_main_profession.is_(True),
            )
            .order_by(ProfessionAssignment.id.desc())
            .first()
        )
        if not assignment:
            return False

        active_temporary_assignments = (
            db.query(ProfessionAssignment)
            .filter(
                ProfessionAssignment.person_id == person_id,
                ProfessionAssignment.is_main_profession.is_(False),
                ProfessionAssignment.is_active.is_(True),
            )
            .all()
        )
        for temp_assignment in active_temporary_assignments:
            temp_assignment.is_active = False
            temp_assignment.end_date = date.today()

        assignment.is_active = True
        assignment.end_date = None
        return True

    @staticmethod
    def _to_person_summary(db: Session, person: Person) -> PersonSummaryResponse:
        profession_name = HumanIntakeService._resolve_profession_for_person(db, person.id)
        return PersonSummaryResponse(
            id=person.id,
            first_name=person.name,
            last_name=person.last_name,
            age=person.age,
            current_status=person.current_status.value,
            health_status=HumanIntakeService._to_api_health_status(person.health_status),
            profession=profession_name or "SIN_ASIGNAR",
            temporary_reassignment=HumanIntakeService._resolve_temporary_reassignment_for_person(db, person.id),
            weight=float(person.weight),
            height=float(person.height),
            camp_id=person.camp_id,
            id_card=person.id_card,
            photo_url=person.photo_url or None,
            background_info=person.background_info,
            is_active=person.is_active,
        )

    @staticmethod
    def _to_person_summary_batched(
        db: Session, person: Person, profession_by_person: dict[int, str], reassignment_by_person: dict[int, str]
    ) -> PersonSummaryResponse:
        profession_name = profession_by_person.get(person.id)
        return PersonSummaryResponse(
            id=person.id,
            first_name=person.name,
            last_name=person.last_name,
            age=person.age,
            current_status=person.current_status.value,
            health_status=HumanIntakeService._to_api_health_status(person.health_status),
            profession=profession_name or "SIN_ASIGNAR",
            temporary_reassignment=reassignment_by_person.get(person.id),
            weight=float(person.weight),
            height=float(person.height),
            camp_id=person.camp_id,
            id_card=person.id_card,
            photo_url=person.photo_url or None,
            background_info=person.background_info,
            is_active=person.is_active,
        )

    @staticmethod
    def _resolve_temporary_reassignment_for_person(db: Session, person_id: int) -> str | None:
        profession_name = (
            db.query(Profession.name)
            .join(ProfessionAssignment, ProfessionAssignment.profession_id == Profession.id)
            .filter(
                ProfessionAssignment.person_id == person_id,
                ProfessionAssignment.is_active.is_(True),
                ProfessionAssignment.is_main_profession.is_(False),
            )
            .order_by(ProfessionAssignment.id.desc())
            .first()
        )
        return profession_name[0] if profession_name else None

    @staticmethod
    def _resolve_profession_for_person(db: Session, person_id: int) -> str | None:
        profession_name = (
            db.query(Profession.name)
            .join(ProfessionAssignment, ProfessionAssignment.profession_id == Profession.id)
            .filter(
                ProfessionAssignment.person_id == person_id,
                ProfessionAssignment.is_active.is_(True),
                ProfessionAssignment.is_main_profession.is_(True),
            )
            .first()
        )
        return profession_name[0] if profession_name else None

    @staticmethod
    def _db_role_to_api_role(db_role_name: str | None) -> str | None:
        if not db_role_name:
            return None

        for api_role_name, mapped_db_role in HumanIntakeService.ROLE_DB_NAMES.items():
            if mapped_db_role == db_role_name:
                return api_role_name
        return None

    @staticmethod
    def _ai_role_to_db_role(ai_role_name: str | None) -> str:
        if not ai_role_name:
            return "SIN_ASIGNAR"
        return HumanIntakeService.ROLE_DB_NAMES.get(ai_role_name.strip(), ai_role_name.strip())

    @staticmethod
    def _normalize_ai_decision(raw_decision: str) -> str:
        normalized = (raw_decision or "").strip().upper()
        if normalized in ("APPROVED", "APROBADO"):
            return "APROBADO"
        if normalized in ("REJECTED", "RECHAZADO"):
            return "RECHAZADO"
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Unsupported AI decision value: {raw_decision}",
        )

    @staticmethod
    def _to_ai_log_summary(log: AILog) -> AILogSummaryResponse:
        context = log.evaluation_context or {}
        score_breakdown_data = context.get("score_breakdown") or {}

        ai_decision = "APROBADO" if log.ai_decision == AIDecisionEnum.APROBADO else "RECHAZADO"
        human_decision = "INGRESO_PERMITIDO" if log.final_user_decision else "INGRESO_RECHAZADO"
        full_name = f"{context.get('first_name', '')} {context.get('last_name', '')}".strip() or "DESCONOCIDO"

        return AILogSummaryResponse(
            id=log.id,
            full_name=full_name,
            ai_decision=ai_decision,
            human_decision=human_decision,
            human_override=(log.ai_decision == AIDecisionEnum.RECHAZADO and log.final_user_decision),
            score=int(context.get("score", 0)),
            explanation=log.decision_reason,
            suggested_profession=HumanIntakeService._ai_role_to_db_role(
                context.get("suggested_profession", "SIN_ASIGNAR")
            ),
            score_breakdown=ScoreBreakdownResponse(
                resilience=int(score_breakdown_data.get("resilience", 0)),
                medical_experience=int(score_breakdown_data.get("medical_experience", 0)),
                defense_experience=int(score_breakdown_data.get("defense_experience", 0)),
                context=int(score_breakdown_data.get("context", 0)),
            ),
            applied_rules=list(context.get("applied_rules", [])),
        )
