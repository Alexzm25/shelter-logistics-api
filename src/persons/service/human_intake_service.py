from datetime import date, datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.ai.enums.ai_decision_enum import AIDecisionEnum
from src.ai.models.ai_log import AILog
from src.ai.service.groq_evaluation_service import GroqEvaluationService
from src.camps.models.camp import Camp  # noqa: F401
from src.persons.enums.current_status_enum import CurrentStatusEnum
from src.persons.enums.health_status_enum import HealthStatusEnum
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
    UpdatePersonRequest,
    UpdatePersonResponse,
    RegisterCandidateRequest,
    RegisterCandidateResponse,
    ScoreBreakdownResponse,
)


class HumanIntakeService:
    ROLE_DB_NAMES = {
        "MEDIC": "MEDICO",
        "SENTINEL": "VIGIA",
        "SCAVENGER": "RECOLECTOR",
        "SUPPORT": "SOPORTE",
    }
    TRACKED_ROLES = ("MEDIC", "SENTINEL", "SCAVENGER", "SUPPORT")

    @staticmethod
    def evaluate_candidate(db: Session, candidate: CandidateInput) -> EvaluationResponse:
        role_counts = HumanIntakeService._get_role_counts(db, candidate.camp_id)
        evaluation = GroqEvaluationService.evaluate_candidate(candidate, role_counts)
        return EvaluationResponse(
            decision=HumanIntakeService._normalize_ai_decision(evaluation.decision),
            score=evaluation.score,
            explanation=evaluation.explanation,
            suggested_profession=HumanIntakeService._ai_role_to_db_role(evaluation.suggested_profession),
            score_breakdown=evaluation.score_breakdown,
            applied_rules=evaluation.applied_rules,
        )

    @staticmethod
    def get_professions(db: Session) -> list[ProfessionOptionResponse]:
        profession_names = db.query(Profession.name).order_by(Profession.name.asc()).all()
        return [ProfessionOptionResponse(name=name) for (name,) in profession_names]

    @staticmethod
    def register_candidate(db: Session, payload: RegisterCandidateRequest) -> RegisterCandidateResponse:
        evaluation = HumanIntakeService.evaluate_candidate(db, payload.candidate)
        allow_entry = payload.human_decision == "PERMITIR_INGRESO"
        selected_profession = (payload.selected_profession or "").strip()

        if allow_entry and not selected_profession:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="A profession must be selected before registration.",
            )

        created_person: Person | None = None
        if allow_entry:
            created_person = Person(
                name=payload.candidate.first_name.strip(),
                last_name=payload.candidate.last_name.strip(),
                age=payload.candidate.age,
                background_info=payload.candidate.background_info.strip(),
                weight=payload.candidate.weight,
                height=payload.candidate.height,
                camp_id=payload.candidate.camp_id,
                current_status=CurrentStatusEnum.LIBRE,
                health_status=HumanIntakeService._infer_health_status(payload.candidate.background_info),
                camp_entry_date=datetime.now(timezone.utc),
                photo_url=(payload.candidate.photo_url or "").strip(),
                is_active=True,
                id_card=(payload.candidate.id_card or "AUTO-GENERATED").strip(),
            )
            db.add(created_person)
            db.flush()

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
            person_id=created_person.id if created_person else None,
            final_user_decision=allow_entry,
        )
        db.add(created_log)

        db.commit()
        db.refresh(created_log)
        if created_person:
            db.refresh(created_person)

        return RegisterCandidateResponse(
            evaluation=evaluation,
            created_person=HumanIntakeService._to_person_summary(db, created_person) if created_person else None,
            created_ai_log=HumanIntakeService._to_ai_log_summary(created_log),
            message="Persona registrada correctamente" if created_person else "Candidato rechazado correctamente",
        )

    @staticmethod
    def get_dashboard(db: Session, camp_id: int) -> DashboardResponse:
        people = db.query(Person).filter(Person.camp_id == camp_id).order_by(Person.id.desc()).all()
        logs = db.query(AILog).filter(AILog.camp_id == camp_id).order_by(AILog.id.desc()).all()

        people_response = [HumanIntakeService._to_person_summary(db, person) for person in people]
        logs_response = [HumanIntakeService._to_ai_log_summary(log) for log in logs]

        return DashboardResponse(people=people_response, ai_logs=logs_response)

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
        person.age = payload.age
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
    def _to_person_summary(db: Session, person: Person) -> PersonSummaryResponse:
        profession_name = HumanIntakeService._resolve_profession_for_person(db, person.id)
        return PersonSummaryResponse(
            id=person.id,
            first_name=person.name,
            last_name=person.last_name,
            age=person.age,
            health_status=HumanIntakeService._to_api_health_status(person.health_status),
            profession=profession_name or "SIN_ASIGNAR",
            temporary_reassignment=None,
            weight=float(person.weight),
            height=float(person.height),
            camp_id=person.camp_id,
            id_card=person.id_card,
            photo_url=person.photo_url or None,
            background_info=person.background_info,
        )

    @staticmethod
    def _resolve_profession_for_person(db: Session, person_id: int) -> str | None:
        profession_name = (
            db.query(Profession.name)
            .join(ProfessionAssignment, ProfessionAssignment.profession_id == Profession.id)
            .filter(
                ProfessionAssignment.person_id == person_id,
                ProfessionAssignment.is_active.is_(True),
            )
            .order_by(ProfessionAssignment.is_main_profession.desc(), ProfessionAssignment.id.desc())
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
