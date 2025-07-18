import logging
from aiogram import Router, F
from aiogram.filters import CommandStart, ChatMemberUpdatedFilter, MEMBER
from aiogram.types import Message, CallbackQuery, ChatMemberUpdated
from sqlalchemy.exc import SQLAlchemyError
from app.api.dao import UserDAO
from app.bot.keyboards import main_menu_keyboard, budget_menu_keyboard, budget_summary_keyboard
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
            name=message.from_user.first_name,
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