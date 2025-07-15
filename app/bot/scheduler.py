import logging
from datetime import date
from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.api.dao import EventDAO, ChatDAO


async def send_daily_events_summary(bot: Bot):
    """
    Отправляет сводку событий на сегодня в заданный чат.
    """
    logging.info("Запуск ежедневных мероприятий...")
    # 1. Найти чат для отправки уведомлений
    target_chat = await ChatDAO.get_notification_target()
    if not target_chat:
        logging.warning("Не найден чат для отправки уведомлений. Пропускаю.")
        return

    # 2. Найти все события на сегодня
    today_events = await EventDAO.find_events_for_date(target_date=date.today())

    # 3. Сформировать и отправить сообщение
    if not today_events:
        message_text = "Доброе утро! ☀️\n\nНа сегодня событий не запланировано."
    else:
        message_text = "Доброе утро! ☀️\n\n**План на сегодня:**\n\n"
        for event in today_events:
            message_text += f"▪️ **{event.title}**\n"
            if event.location:
                message_text += f"   📍 {event.location}\n"
        message_text += "\nВсем продуктивного дня!"

    try:
        await bot.send_message(
            chat_id=target_chat.chat_id,
            text=message_text
        )
        logging.info(f"Отправлена сводка событий в чат {target_chat.chat_title}")
    except Exception as e:
        logging.error(f"Не удалось отправить сообщение в чат {target_chat.chat_id}: {e}")


# Создаем экземпляр планировщика
scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
