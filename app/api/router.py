import logging
from fastapi import APIRouter, HTTPException
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from app.api.dao import EventDAO, ContractorDAO
from app.api.schemas import EventData, ContractorData

router = APIRouter(prefix='/api', tags=['API'])


@router.post("/event", response_class=JSONResponse)
async def create_event(request: Request):
    # Получаем и валидируем JSON данные
    data = await request.json()
    valid_data = EventData(**data)
    try:
        # Добавление мероприятия в базу данных
        await EventDAO.add(
            title=valid_data.title,
            event_date=valid_data.event_date,
            location=valid_data.location,
            user_id=valid_data.user_id
        )
        return {"status": "success", "message": "Event created successfully"}
    except Exception as e:
        logging.error(f"DB Error on adding event: {e}")


@router.put("/event/{event_id}", response_class=JSONResponse)
async def update_event(event_id: int, request: Request):
    try:
        # Получаем и валидируем JSON данные
        data = await request.json()
        valid_data = EventData(**data)

        # Проверка существования мероприятия
        existing_event = await EventDAO.find_one_or_none(id=event_id)
        if not existing_event:
            raise HTTPException(status_code=404, detail="Event not found")

        # Обновление мероприятия
        updated_event = await EventDAO.update(
            id=event_id,
            title=valid_data.title,
            event_date=valid_data.event_date,
            location=valid_data.location,
            user_id=valid_data.user_id
        )
        if not updated_event:
            raise HTTPException(status_code=500, detail="Failed to update event")

        return {"status": "success", "message": "Event updated successfully", "event_id": event_id}

    except HTTPException as he:
        raise he
    except Exception as e:
        logging.error(f"DB Error on updating event: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/event/{event_id}", response_class=JSONResponse)
async def delete_event(event_id: int):
    try:
        # Проверка существования мероприятия
        existing_event = await EventDAO.find_one_or_none(id=event_id)
        if not existing_event:
            raise HTTPException(status_code=404, detail="Event not found")

        # Удаление мероприятия
        success = await EventDAO.delete(id=event_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete event")

        return {"status": "success", "message": "Event deleted successfully", "event_id": event_id}

    except HTTPException as he:
        raise he
    except Exception as e:
        logging.error(f"DB Error on deleting event: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/contractor", response_class=JSONResponse)
async def create_contractor(request: Request):
    # Получаем и валидируем JSON данные
    data = await request.json()
    valid_data = ContractorData(**data)
    try:
        # Добавление подрядчика в базу данных
        await ContractorDAO.add(
            name=valid_data.name,
            category=valid_data.category,
            contact=valid_data.contact,
            owner_id=valid_data.owner_id
        )
        return {"status": "success", "message": "Contractor created successfully"}
    except Exception as e:
        logging.error(f"DB Error on adding contractor: {e}")


@router.put("/contractor/{contractor_id}", response_class=JSONResponse)
async def update_contractor(contractor_id: int, request: Request):
    try:
        # Получаем и валидируем JSON данные
        data = await request.json()
        valid_data = ContractorData(**data)

        # Проверка существования подрядчика
        existing_contractor = await ContractorDAO.find_one_or_none(id=contractor_id)
        if not existing_contractor:
            raise HTTPException(status_code=404, detail="Contractor not found")

        # Обновление подрядчика
        updated_contractor = await ContractorDAO.update(
            id=contractor_id,
            name=valid_data.name,
            category=valid_data.category,
            contact=valid_data.contact
        )
        if not updated_contractor:
            raise HTTPException(status_code=500, detail="Failed to update contractor")

        return {"status": "success", "message": "Contractor updated successfully", "contractor_id": contractor_id}

    except HTTPException as he:
        raise he
    except Exception as e:
        logging.error(f"DB Error on updating contractor: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/contractor/{contractor_id}", response_class=JSONResponse)
async def delete_contractor(contractor_id: int):
    try:
        # Проверка существования подрядчика
        existing_contractor = await ContractorDAO.find_one_or_none(id=contractor_id)
        if not existing_contractor:
            raise HTTPException(status_code=404, detail="Contractor not found")

        # Удаление подрядчика
        success = await ContractorDAO.delete(id=contractor_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete contractor")

        return {"status": "success", "message": "Contractor deleted successfully", "contractor_id": contractor_id}

    except HTTPException as he:
        raise he
    except Exception as e:
        logging.error(f"DB Error on deleting contractor: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
