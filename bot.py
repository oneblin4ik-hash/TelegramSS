import asyncio
import logging
import os
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import (
    CallbackQuery,
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "8950032855:AAF3puz71ztCKrXMJEdgq8je9K8Cjr7EhOg")

BASE_DIR = Path(__file__).parent
GUIDES_DIR = BASE_DIR / "guides"

GUIDES = {
    "kbju": ("📊 КБЖУ — как считать", "kbju.pdf"),
    "anti_otek": ("💧 Анти-отёк", "anti_otek.pdf"),
    "dnevnik": ("📓 Дневник питания", "dnevnik.pdf"),
    "motivation": ("🔥 Мотивация", "motivation.pdf"),
    "sovetov": ("✅ 13 советов", "13_sovetov.pdf"),
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

dp = Dispatcher()


def main_menu() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=title, callback_data=f"guide:{key}")]
        for key, (title, _) in GUIDES.items()
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


@dp.message(CommandStart())
async def on_start(message: Message) -> None:
    await message.answer(
        f"Привет, <b>{message.from_user.first_name}</b>! 👋\n\n"
        "Выбери гайд — пришлю его PDF-файлом:",
        reply_markup=main_menu(),
    )


@dp.callback_query(F.data.startswith("guide:"))
async def on_guide(callback: CallbackQuery) -> None:
    key = callback.data.split(":", 1)[1]
    item = GUIDES.get(key)
    if not item:
        await callback.answer("Гайд не найден", show_alert=True)
        return

    title, filename = item
    path = GUIDES_DIR / filename
    if not path.exists():
        logger.error("Файл не найден: %s", path)
        await callback.answer("Файл временно недоступен", show_alert=True)
        return

    await callback.answer("Отправляю...")
    await callback.message.answer_document(FSInputFile(path), caption=title)


async def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN не задан")

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    logger.info("Бот запускается...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен")
