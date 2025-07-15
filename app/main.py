import logging
from contextlib import asynccontextmanager
from app.bot.create import bot, dp, stop_bot, start_bot
from app.bot.router import router
from app.config import settings
from aiogram.types import Update
from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.pages.router import router as router_pages
from app.api.router import router as router_API

# Инициализация логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Подключение Jinja2 для рендеринга HTML
templates = Jinja2Templates(directory="app/templates")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Starting bot setup...")
    dp.include_router(router)

    try:
        await start_bot()
        webhook_url = settings.get_webhook_url()
        await bot.set_webhook(url=webhook_url,
                              allowed_updates=dp.resolve_used_update_types(),
                              drop_pending_updates=True)
        logging.info(f"Webhook set to {webhook_url}")
    except Exception as e:
        logging.error(f"Error during bot setup: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Bot setup failed.")

    yield
    logging.info("Shutting down bot...")
    try:
        await bot.delete_webhook()
        await stop_bot()
        logging.info("Webhook deleted and bot stopped successfully.")
    except Exception as e:
        logging.error(f"Error during bot shutdown: {e}", exc_info=True)


app = FastAPI(lifespan=lifespan)
app.include_router(router_pages)
app.include_router(router_API)
# Поддержка статических файлов
app.mount('/static', StaticFiles(directory='app/static'), name='static')


@app.post("/webhook")
async def webhook(request: Request) -> None:
    try:
        json_data = await request.json()
        await dp.feed_webhook_update(bot, Update(**json_data))
    except Exception as e:
        logging.error(f"Error processing update: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail="Failed to process webhook update.")
