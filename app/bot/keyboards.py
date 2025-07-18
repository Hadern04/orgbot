from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, WebAppInfo
from app.config import settings


# --- Стартовое меню и навигация ---
def main_menu_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Главное меню."""
    kb = InlineKeyboardBuilder()
    url_events = f"{settings.BASE_SITE}/events?user_id={user_id}"
    url_contractors = f"{settings.BASE_SITE}/contractors?user_id={user_id}"
    url_tasks = f"{settings.BASE_SITE}/tasks?user_id={user_id}"
    url_checklists = f"{settings.BASE_SITE}/checklists?user_id={user_id}"
    kb.button(text="🗓 Календарь событий", web_app=WebAppInfo(url=url_events))
    kb.button(text="👥 Подрядчики", web_app=WebAppInfo(url=url_contractors))
    kb.button(text="📋 Чек-листы", web_app=WebAppInfo(url=url_checklists))
    kb.button(text="💰 Бюджет", callback_data="budget_menu")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


# --- Информация о бюджете
def budget_menu_keyboard() -> InlineKeyboardMarkup:
    """Меню работы с бюджетом."""
    kb = InlineKeyboardBuilder()
    kb.button(text="📊 Общая сводка", callback_data="budget_summary")
    kb.button(text="📁 Открыть Google Sheet",
              url="https://docs.google.com/spreadsheets/d/1UJS5Ndx8IYD0q6uSeJbzUyGzGMGxSobSIYE1EpEFwIc/edit?usp=sharing")
    kb.button(text="⬅️ Назад", callback_data="back_to_main_menu")
    kb.adjust(1)
    return kb.as_markup()


def budget_summary_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура после вывода сводки по бюджету."""
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ Назад", callback_data="budget_menu")
    kb.adjust(1)
    return kb.as_markup()
