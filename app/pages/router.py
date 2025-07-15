import logging
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from app.api.dao import UserDAO, EventDAO, ContractorDAO

router = APIRouter(prefix='', tags=['Фронтенд'])
templates = Jinja2Templates(directory='app/templates')


@router.get('/events', response_class=HTMLResponse)
async def read_root(request: Request, user_id):
    data_page = {'request': request, 'access': False, 'title_h1': 'Мои мероприятия', 'events': []}
    user = await UserDAO.find_one_or_none(telegram_id=user_id)

    if user_id is None or user is None:
        data_page[
            'message'] = 'Пользователь, по которому нужно отобразить данные, не указан или не найден в базе данных'
        return templates.TemplateResponse('events.html', data_page)
    data_page['user_id'] = user.id

    events = await EventDAO.get_events_by_user(user_id=user.id)

    data_page['access'] = True
    if events:
        serialized_events = [
            {
                'event_id': event['event_id'],
                'event_title': event['event_title'],
                'event_date': event['event_date'].isoformat(),
                'event_location': event['event_location'],
                'user_id': event['user_id']
            }
            for event in events
        ]
        data_page['events'] = serialized_events
    return templates.TemplateResponse('events.html', data_page)


@router.get('/contractors', response_class=HTMLResponse)
async def read_root(request: Request, user_id):
    try:
        data_page = {'request': request, 'access': False, 'title_h1': 'Список подрядчиков', 'categories': [], 'contractors': []}

        user = await UserDAO.find_one_or_none(telegram_id=user_id)
        if user_id is None or user is None:
            data_page[
                'message'] = 'Пользователь, по которому нужно отобразить данные, не указан или не найден в базе данных'
            return templates.TemplateResponse('contractors.html', data_page)
        data_page['user_id'] = user.id

        categories = await ContractorDAO.get_all_categories()
        contractors = await ContractorDAO.get_all_accessible_contractors(user_id=user.id)

        data_page['access'] = True
        if categories:
            data_page['categories'] = categories
        if contractors and categories:
            data_page['contractors'] = [
                {
                    'id': contractor['id'],
                    'contractor_name': contractor['name'],
                    'contractor_category': contractor['category'],
                    'contractor_contact': contractor['contact'] or 'Не указан',
                    'contractor_owner_id': contractor['owner_id']
                }
                for contractor in contractors
            ]
        return templates.TemplateResponse('contractors.html', data_page)
    except Exception as e:
        logging.error(f'Error in /contractors endpoint: {str(e)}')

        data_page = {'error': 'Произошла ошибка при загрузке данных'}
        return templates.TemplateResponse('contractors.html', data_page)

