from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, WebAppInfo
from app.config import settings


# --- Стартовое меню и навигация ---
def main_menu_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Главное меню."""
    kb = InlineKeyboardBuilder()
    url_events = f"{settings.BASE_SITE}/events?user_id={user_id}"
    url_contractors = f"{settings.BASE_SITE}/contractors?user_id={user_id}"
    kb.button(text="🗓 Календарь событий", web_app=WebAppInfo(url=url_events))
    kb.button(text="👥 Подрядчики", web_app=WebAppInfo(url=url_contractors))
    kb.button(text="💰 Бюджет", callback_data="budget_menu")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


# --- Календарь событий ---
def calendar_keyboard() -> InlineKeyboardMarkup:
    """Меню календаря с кнопкой 'Назад'."""
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ Назад", callback_data="back_to_main_menu")
    return kb.as_markup()


# --- Справочник подрядчиков ---
def contractors_menu_keyboard(categories: list[str]) -> InlineKeyboardMarkup:
    """Меню со списком категорий подрядчиков."""
    kb = InlineKeyboardBuilder()
    for category in categories:
        kb.button(text=category, callback_data=f"contractor_category_{category}")
    kb.button(text="⬅️ Назад", callback_data="back_to_main_menu")
    kb.adjust(2)  # 2 кнопки в ряд
    return kb.as_markup()


def contractors_list_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для списка подрядчиков (только кнопка 'Назад')."""
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ Назад", callback_data="contractors_menu")
    return kb.as_markup()


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
