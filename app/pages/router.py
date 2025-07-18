import logging

from fastapi import APIRouter, HTTPException
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.api.dao import UserDAO

router = APIRouter(prefix='', tags=['Фронтенд'])
templates = Jinja2Templates(directory='app/templates')


async def get_user_or_error(user_id: int):
    """Вспомогательная функция для получения пользователя"""
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID is required")

    user = await UserDAO.find_one_or_none(telegram_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get('/events', response_class=HTMLResponse)
async def get_events_page(request: Request, user_id: int):
    """Получение страницы с мероприятиями пользователя"""
    template = 'events.html'
    try:
        user = await get_user_or_error(user_id)

        return templates.TemplateResponse(
            template,
            {
                'request': request,
                'access': True,
                'title_h1': 'Мои мероприятия',
                'user_id': user.id
            }
        )

    except HTTPException:
        return templates.TemplateResponse(
            template,
            {
                'request': request,
                'access': False,
                'title_h1': 'Мои мероприятия',
                'message': 'Пользователь не найден или не указан'
            }
        )
    except Exception as e:
        logging.error(f'Error in events endpoint: {str(e)}')
        return templates.TemplateResponse(
            template,
            {
                'request': request,
                'access': False,
                'title_h1': 'Мои мероприятия',
                'message': 'Произошла ошибка при загрузке данных'
            }
        )


@router.get('/contractors', response_class=HTMLResponse)
async def get_contractors_page(request: Request, user_id: int):
    """Получение страницы с подрядчиками"""
    template = 'contractors.html'
    try:
        user = await get_user_or_error(user_id)
        return templates.TemplateResponse(
            template,
            {
                'request': request,
                'access': True,
                'title_h1': 'Список подрядчиков',
                'user_id': user.id
            }
        )

    except HTTPException:
        return templates.TemplateResponse(
            template,
            {
                'request': request,
                'access': False,
                'title_h1': 'Список подрядчиков',
                'message': 'Пользователь не найден или не указан'
            }
        )
    except Exception as e:
        logging.error(f'Error in contractors endpoint: {str(e)}')
        return templates.TemplateResponse(
            template,
            {
                'request': request,
                'access': False,
                'title_h1': 'Список подрядчиков',
                'message': 'Произошла ошибка при загрузке данных'
            }
        )


@router.get('/tasks', response_class=HTMLResponse)
async def get_tasks_page(request: Request, user_id: int):
    """Получение страницы с мероприятиями пользователя"""
    template = 'tasks.html'
    try:
        user = await get_user_or_error(user_id)
        return templates.TemplateResponse(
            template,
            {
                'request': request,
                'access': True,
                'title_h1': 'Мои мероприятия',
                'user_id': user.id
            }
        )

    except HTTPException:
        return templates.TemplateResponse(
            template,
            {
                'request': request,
                'access': False,
                'title_h1': 'Мои мероприятия',
                'message': 'Пользователь не найден или не указан'
            }
        )
    except Exception as e:
        logging.error(f'Error in tasks endpoint: {str(e)}')
        return templates.TemplateResponse(
            template,
            {
                'request': request,
                'access': False,
                'title_h1': 'Мои мероприятия',
                'message': 'Произошла ошибка при загрузке данных'
            }
        )


@router.get('/checklists', response_class=HTMLResponse)
async def get_checklists_page(request: Request, user_id: int):
    """Получение страницы с мероприятиями пользователя"""
    template = 'checklists.html'
    try:
        user = await get_user_or_error(user_id)
        return templates.TemplateResponse(
            template,
            {
                'request': request,
                'access': True,
                'title_h1': 'Мои мероприятия',
                'user_id': user.id
            }
        )

    except HTTPException:
        return templates.TemplateResponse(
            template,
            {
                'request': request,
                'access': False,
                'title_h1': 'Мои мероприятия',
                'message': 'Пользователь не найден или не указан'
            }
        )
    except Exception as e:
        logging.error(f'Error in checklists endpoint: {str(e)}')
        return templates.TemplateResponse(
            template,
            {
                'request': request,
                'access': False,
                'title_h1': 'Мои мероприятия',
                'message': 'Произошла ошибка при загрузке данных'
            }
        )
