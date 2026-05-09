from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from src.inventory.enums import MovementTypeEnum
from src.inventory.models.inventory import Inventory
from src.inventory.models.inventory_movement import InventoryMovement
from src.inventory.models.inventory_resource import InventoryResource
from src.persons.models.person import Person
from src.persons.models.profession import Profession
from src.persons.models.profession_assignment import ProfessionAssignment
from src.production.models.production_log import ProductionLog
from src.production.schemas.production_request import RegisterProductionRequest
from src.production.schemas.production_response import RegisterProductionResponse


class ProductionService:
    @staticmethod
    def register_production(
        db: Session,
        person_id: int,
        payload: RegisterProductionRequest,
    ) -> RegisterProductionResponse:
        person = db.query(Person).filter(Person.id == person_id).first()

        if not person:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Persona no encontrada",
            )

        profession_assignment = (
            db.query(ProfessionAssignment)
            .filter(
                ProfessionAssignment.person_id == person.id,
                ProfessionAssignment.is_active == True,
                ProfessionAssignment.is_main_profession == True,
            )
            .first()
        )

        if not profession_assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La persona no tiene una profesión activa",
            )

        profession = (
            db.query(Profession)
            .filter(Profession.id == profession_assignment.profession_id)
            .first()
        )

        if not profession:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profesión no encontrada",
            )

        inventory = (
            db.query(Inventory)
            .filter(Inventory.camp_id == person.camp_id)
            .first()
        )

        if not inventory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inventario del campamento no encontrado",
            )

        inventory_resource = (
            db.query(InventoryResource)
            .filter(
                InventoryResource.inventory_id == inventory.id,
                InventoryResource.resource_id == payload.resource_id,
            )
            .first()
        )

        if not inventory_resource:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recurso no encontrado en el inventario del campamento",
            )

        production_log = ProductionLog(
            actual_quantity=payload.actual_quantity,
            expected_quantity=payload.actual_quantity,
            camp_id=person.camp_id,
            person_id=person.id,
            resource_id=payload.resource_id,
            profession_id=profession.id,
        )

        inventory_resource.quantity += payload.actual_quantity

        inventory_movement = InventoryMovement(
            quantity=payload.actual_quantity,
            inventory_resource_id=inventory_resource.id,
            movement_type=MovementTypeEnum.INGRESO,
            transfer_request_id=None,
        )

        db.add(production_log)
        db.add(inventory_movement)
        db.commit()

        return RegisterProductionResponse(
            message="Producción registrada correctamente",
        )