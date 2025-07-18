import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Request, Query
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.api.dao import (
    EventDAO,
    ContractorDAO,
    ContractorCategoryDAO,
    ChecklistItemDAO,
    ChecklistDAO
)

router = APIRouter(prefix='/api', tags=['API'])


# ========== Events Endpoints ==========
@router.get("/events", response_class=JSONResponse)
async def get_events(owner_id: int):
    """Get all events for specified owner"""
    try:
        events = await EventDAO.find_all(owner_id=owner_id)
        return events
    except SQLAlchemyError as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error")


@router.post("/events", response_class=JSONResponse)
async def create_event(request: Request):
    """Create new event"""
    try:
        data = await request.json()

        existing = await EventDAO.find_one_or_none(**data)
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Мероприятие с таким названием уже существует"
            )

        data["date"] = datetime.strptime(data["date"], '%Y-%m-%d').date()
        await EventDAO.add(**data)
        return {"status": "success", "message": "Event created successfully"}

    except Exception as e:
        logging.error(f"DB Error on adding event: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/events/{event_id}", response_class=JSONResponse)
async def update_event(event_id: int, request: Request):
    """Update existing event"""
    try:
        data = await request.json()

        existing_event = await EventDAO.find_one_or_none(id=event_id)
        if not existing_event:
            raise HTTPException(status_code=404, detail="Event not found")

        data["date"] = datetime.strptime(data["date"], '%Y-%m-%d').date()
        updated_event = await EventDAO.update(id=event_id, **data)

        if not updated_event:
            raise HTTPException(status_code=500, detail="Failed to update event")

        return {
            "status": "success",
            "message": "Event updated successfully",
            "event_id": event_id
        }

    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=ve.errors())
    except Exception as e:
        logging.error(f"DB Error on updating event: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/events/{event_id}", response_class=JSONResponse)
async def delete_event(event_id: int):
    """Delete event by ID"""
    try:
        existing_event = await EventDAO.find_one_or_none(id=event_id)
        if not existing_event:
            raise HTTPException(status_code=404, detail="Event not found")

        success = await EventDAO.delete(id=event_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete event")

        return {
            "status": "success",
            "message": "Event deleted successfully",
            "event_id": event_id
        }
    except Exception as e:
        logging.error(f"DB Error on deleting event: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ========== Contractors Endpoints ==========
@router.get("/contractors", response_class=JSONResponse)
async def get_contractors(
        owner_id: int,
        category: Optional[int] = Query(None)
):
    """Get all contractors with optional category filter"""
    try:
        filters = {'owner_id': owner_id}
        if category is not None:
            filters['category_id'] = category

        contractors = await ContractorDAO.find_all(**filters)
        return contractors
    except SQLAlchemyError as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error")


@router.post("/contractors", response_class=JSONResponse)
async def create_contractor(request: Request):
    """Create new contractor"""
    try:
        data = await request.json()

        existing = await ContractorDAO.find_one_or_none(**data)
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Такой подрядчик уже существует"
            )

        contractor = await ContractorDAO.add(
            name=data['name'],
            category_id=data['category_id'],
            contact=data['contact'],
            owner_id=data['owner_id']
        )
        return contractor
    except Exception as e:
        logging.error(f"DB Error on adding contractor: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/contractors/{contractor_id}", response_class=JSONResponse)
async def update_contractor(contractor_id: int, request: Request):
    """Update existing contractor"""
    try:
        data = await request.json()

        existing = await ContractorDAO.find_one_or_none(id=contractor_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Contractor not found")

        if 'category_id' in data:
            category = await ContractorCategoryDAO.find_one_or_none(
                id=data['category_id']
            )
            if not category:
                raise HTTPException(status_code=400, detail="Category not found")

        updated = await ContractorDAO.update(id=contractor_id, **data)
        if not updated:
            raise HTTPException(
                status_code=500,
                detail="Failed to update contractor"
            )

        return {
            "status": "success",
            "message": "Contractor updated successfully",
            "contractor_id": contractor_id
        }
    except SQLAlchemyError as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error")


@router.delete("/contractors/{contractor_id}", response_class=JSONResponse)
async def delete_contractor(contractor_id: int):
    """Delete contractor by ID"""
    try:
        existing = await ContractorDAO.find_one_or_none(id=contractor_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Contractor not found")

        success = await ContractorDAO.delete(id=contractor_id)
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to delete contractor"
            )

        return {
            "status": "success",
            "message": "Contractor deleted",
            "contractor_id": contractor_id
        }
    except SQLAlchemyError as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error")


# ========== Contractor Categories Endpoints ==========
@router.post("/contractor-categories", response_class=JSONResponse)
async def create_category(request: Request):
    """Create new contractor category"""
    try:
        data = await request.json()

        existing = await ContractorCategoryDAO.find_one_or_none(**data)
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Категория с таким названием уже существует"
            )

        category = await ContractorCategoryDAO.add(
            title=data['title'],
            owner_id=data['owner_id']
        )
        return category
    except SQLAlchemyError as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error")


@router.get("/contractor-categories", response_class=JSONResponse)
async def get_categories(owner_id: int):
    """Get all contractor categories for specified owner"""
    try:
        categories = await ContractorCategoryDAO.find_all(owner_id=owner_id)
        return categories
    except SQLAlchemyError as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error")


@router.delete("/contractor-categories/{category_id}", response_class=JSONResponse)
async def delete_category(category_id: int):
    """Delete contractor category by ID"""
    try:
        existing = await ContractorCategoryDAO.find_one_or_none(id=category_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Category not found")

        success = await ContractorCategoryDAO.delete(id=category_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete category")

        return {
            "status": "success",
            "message": "Contractor deleted",
            "category_id": category_id
        }
    except SQLAlchemyError as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error")


# ========== Checklists Endpoints ==========
@router.get("", response_class=JSONResponse)
async def get_checklists(owner_id: int):
    """Get all checklists for specified owner with items"""
    try:
        checklists = await ChecklistDAO.find_all(owner_id=owner_id)

        for checklist in checklists:
            items = await ChecklistItemDAO.find_all(checklist_id=checklist["id"])
            checklist["items"] = items

        return checklists
    except SQLAlchemyError as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error")


@router.get("/{checklist_id}", response_class=JSONResponse)
async def get_checklist(checklist_id: int):
    """Get specific checklist by ID with items"""
    try:
        checklist = await ChecklistDAO.find_one_or_none(id=checklist_id)
        if not checklist:
            raise HTTPException(status_code=404, detail="Checklist not found")

        items = await ChecklistItemDAO.find_all(checklist_id=checklist_id)
        checklist["items"] = items

        return checklist
    except SQLAlchemyError as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error")


@router.post("", response_class=JSONResponse)
async def create_checklist(request: Request):
    """Create new checklist with items"""
    try:
        data = await request.json()

        if "event_id" in data:
            existing_event = await EventDAO.find_one_or_none(id=data["event_id"])
            if not existing_event:
                raise HTTPException(status_code=404, detail="Event not found")

        if "deadline" in data:
            data["deadline"] = datetime.strptime(data["deadline"], '%Y-%m-%d').date()

        checklist_id = await ChecklistDAO.add(**data)

        if "items" in data:
            for item in data["items"]:
                await ChecklistItemDAO.add(
                    checklist_id=checklist_id,
                    text=item["text"],
                    completed=item.get("completed", False)
                )

        return {
            "status": "success",
            "message": "Checklist created successfully",
            "checklist_id": checklist_id
        }
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=ve.errors())
    except Exception as e:
        logging.error(f"DB Error on creating checklist: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{checklist_id}", response_class=JSONResponse)
async def update_checklist(checklist_id: int, request: Request):
    """Update existing checklist and its items"""
    try:
        data = await request.json()

        existing_checklist = await ChecklistDAO.find_one_or_none(id=checklist_id)
        if not existing_checklist:
            raise HTTPException(status_code=404, detail="Checklist not found")

        if "deadline" in data:
            data["deadline"] = datetime.strptime(data["deadline"], '%Y-%m-%d').date()

        updated_checklist = await ChecklistDAO.update(id=checklist_id, **data)

        if "items" in data:
            await ChecklistItemDAO.delete_all_for_checklist(checklist_id)
            for item in data["items"]:
                await ChecklistItemDAO.add(
                    checklist_id=checklist_id,
                    text=item["text"],
                    completed=item.get("completed", False)
                )

        return {
            "status": "success",
            "message": "Checklist updated successfully",
            "checklist_id": checklist_id
        }
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=ve.errors())
    except Exception as e:
        logging.error(f"DB Error on updating checklist: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{checklist_id}", response_class=JSONResponse)
async def delete_checklist(checklist_id: int):
    """Delete checklist and all its items"""
    try:
        existing_checklist = await ChecklistDAO.find_one_or_none(id=checklist_id)
        if not existing_checklist:
            raise HTTPException(status_code=404, detail="Checklist not found")

        await ChecklistItemDAO.delete_all_for_checklist(checklist_id)
        success = await ChecklistDAO.delete(id=checklist_id)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete checklist")

        return {
            "status": "success",
            "message": "Checklist deleted successfully",
            "checklist_id": checklist_id
        }
    except Exception as e:
        logging.error(f"DB Error on deleting checklist: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
