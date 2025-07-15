import logging
from datetime import datetime
from aiogram import Router, F
from aiogram.filters import Command, CommandStart, ChatMemberUpdatedFilter, MEMBER
from aiogram.types import Message, CallbackQuery, ChatMemberUpdated
from sqlalchemy.exc import SQLAlchemyError
from app.api.dao import UserDAO, EventDAO, ContractorDAO, ChatDAO
from app.bot.keyboards import main_menu_keyboard, calendar_keyboard, contractors_menu_keyboard, contractors_list_keyboard, \
    budget_menu_keyboard, budget_summary_keyboard
from app.bot.table import get_budget_info

router = Router()


# --- Стартовое меню и навигация ---
async def greet_user(message: Message, is_new_user: bool) -> None:
    """Приветствует пользователя и отправляет главное меню."""
    greeting = "Добро пожаловать" if is_new_user else "С возвращением"
    await message.answer(
        f"{greeting}, <b>{message.from_user.full_name}</b>!\n\n"
        "Я ваш ассистент по организации мероприятий. Чем могу помочь?",
        reply_markup=main_menu_keyboard(user_id=message.from_user.id)
    )


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Обрабатывает команду /start, регистрирует пользователя, если он новый."""
    user = await UserDAO.find_one_or_none(telegram_id=message.from_user.id)
    if not user:
        await UserDAO.add(
            telegram_id=message.from_user.id,
            first_name=message.from_user.first_name,
            username=message.from_user.username
        )

    await greet_user(message, is_new_user=not user)


@router.callback_query(F.data == "back_to_main_menu")
async def back_to_main_menu(callback: CallbackQuery):
    """Возвращает в главное меню."""
    await callback.message.edit_text(
        "Чем я могу помочь вам сегодня?",
        reply_markup=main_menu_keyboard(user_id=callback.from_user.id)
    )
    await callback.answer()


# --- Календарь событий ---
@router.callback_query(F.data == "calendar_view")
async def view_calendar(callback: CallbackQuery):
    """Показывает календарь событий пользователя."""
    user = await UserDAO.find_one_with_events(telegram_id=callback.from_user.id)
    events = user.events

    if not events:
        text = "🗓 Ваш календарь событий пока пуст.\n\n"
    else:
        text = "🗓 Ваши предстоящие события:\n\n"
        sorted_events = sorted(events, key=lambda x: x.event_date)
        for event in sorted_events:
            text += f"▪️ {event.title}\n"
            text += f"        Дата: {event.event_date.strftime('%d.%m.%Y')}\n"
            if event.location:
                text += f"        Место: {event.location}\n"
            text += "\n"

    text += "Чтобы добавить событие, используйте команду:\n`/add Название, ДД.ММ.ГГГГ, Место (необязательно)`"
    await callback.message.edit_text(text, reply_markup=calendar_keyboard(), parse_mode='Markdown')
    await callback.answer()


@router.message(Command("add"))
async def add_event(message: Message):
    """Добавляет новое событие."""
    user = await UserDAO.find_one_or_none(telegram_id=message.from_user.id)
    try:
        # Убираем /add из строки
        args_str = message.text.split(maxsplit=1)[1]
        parts = [p.strip() for p in args_str.split(',')]
        title = parts[0]
        date_str = parts[1]
        location = parts[2] if len(parts) > 2 else None

        if not title or not date_str:
            raise ValueError()

        event_date = datetime.strptime(date_str, "%d.%m.%Y").date()

        await EventDAO.add(
            title=title,
            event_date=event_date,
            location=location,
            user_id=user.id
        )
        await message.reply(f"✅ Событие '{title}' успешно добавлено на {date_str}!")

    except (IndexError, ValueError):
        await message.reply(
            "❌ Ошибка! Неверный формат.\n\n"
            "Используйте формат: `/add Название, ДД.ММ.ГГГГ, Место проведения`\n"
            "Место проведения можно не указывать.\n\n"
            "Пример: `/add Конференция, 25.10.2025, Москва`",
            parse_mode='Markdown'
        )
    except SQLAlchemyError as e:
        logging.error(f"DB Error on adding event: {e}")
        await message.reply("Произошла ошибка при добавлении события в базу данных.")


# --- Справочник подрядчиков ---
@router.callback_query(F.data == "contractors_menu")
async def show_contractors_menu(callback: CallbackQuery):
    """Показывает меню с категориями подрядчиков."""

    logging.info("Callback 'contractors_menu' received.")
    categories = await ContractorDAO.get_all_categories()
    logging.info(f"Retrieved categories: {categories}")

    if not categories:
        await callback.answer("Справочник подрядчиков пока пуст.", show_alert=True)
        return

    await callback.message.edit_text(
        "👥 Справка по подрядчикам\n\nВыберите категорию:",
        reply_markup=contractors_menu_keyboard(categories)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("contractor_category_"))
async def show_contractor_list(callback: CallbackQuery):
    """Показывает список подрядчиков в выбранной категории."""

    category = callback.data.split('_')[-1]
    contractors = await ContractorDAO.find_all(category=category)

    text = f"👥 {category}:\n\n"
    if not contractors:
        text += "В этой категории пока нет записей."
    else:
        for contractor in contractors:
            text += f"▪️ Имя/Название: {contractor.name}\n"
            text += f"        Контакт: {contractor.contact}\n\n"

    await callback.message.edit_text(
        text,
        reply_markup=contractors_list_keyboard()
    )
    await callback.answer()


# --- Информация о бюджете
@router.callback_query(F.data == "budget_menu")
async def budget_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "💰 Управление бюджетом мероприятия:",
        reply_markup=budget_menu_keyboard()
    )


@router.callback_query(F.data == "budget_summary")
async def show_budget_summary(callback: CallbackQuery):
    gsheet_key = '1UJS5Ndx8IYD0q6uSeJbzUyGzGMGxSobSIYE1EpEFwIc'
    try:
        result = get_budget_info(gsheet_key)
        await callback.message.edit_text(
            result,
            reply_markup=budget_summary_keyboard()
        )
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}", show_alert=True)


# --- Управление чатами ---
@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER))
async def on_new_chat_member(event: ChatMemberUpdated):
    """Автоматически сохраняет чат, когда бота добавляют в новую группу."""
    chat_info = event.chat
    try:
        existing_chat = await ChatDAO.find_one_or_none(chat_id=chat_info.id)
        if not existing_chat:
            await ChatDAO.add(
                chat_id=chat_info.id,
                chat_title=chat_info.title
            )
            logging.info(f"Бот добавлен в новый чат: {chat_info.title} (ID: {chat_info.id})")
    except SQLAlchemyError as e:
        logging.error(f"Ошибка при добавлении чата в БД: {e}")
