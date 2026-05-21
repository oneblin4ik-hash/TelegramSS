import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher, F, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

# ---------- Конфиг (всё из переменных окружения Render) ----------
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN env var is not set")

# Render автоматически прокидывает RENDER_EXTERNAL_URL вида https://your-service.onrender.com
BASE_URL = os.getenv("WEBHOOK_BASE_URL") or os.getenv("RENDER_EXTERNAL_URL")
if not BASE_URL:
    raise RuntimeError(
        "Neither WEBHOOK_BASE_URL nor RENDER_EXTERNAL_URL is set. "
        "On Render, RENDER_EXTERNAL_URL is provided automatically for Web Services."
    )

WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{BASE_URL.rstrip('/')}{WEBHOOK_PATH}"

# Простейший секрет для верификации входящих запросов от Telegram.
# Telegram будет слать его в заголовке X-Telegram-Bot-Api-Secret-Token.
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "serbolin-secret-change-me")

# Render задаёт PORT сам. Web Service ОБЯЗАН слушать этот порт.
PORT = int(os.getenv("PORT", "10000"))

# ---------- Bot & Dispatcher ----------
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


# ---------- FSM ----------
class GameState(StatesGroup):
    start = State()
    gender = State()
    age = State()


def make_reply_kb(buttons: list[str]) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for b in buttons:
        builder.add(KeyboardButton(text=b))
    return builder.as_markup(resize_keyboard=True)


# ---------- Handlers ----------
@dp.message(F.text == "/start")
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🔮 *САГА О ПОТЕРЯННОМ ПРЕССЕ* 🔮\n"
        "Добро пожаловать в Фитосферу, странник.\n"
        "Я — магистр Serbolin.\n"
        "Злой колдун Великий Пельменес украл твой пресс и спрятал его в шести землях.\n"
        "Готов отправиться в поход за своими кубиками?",
        reply_markup=make_reply_kb(["⚔️ Да, вернуть пресс!"]),
    )
    await state.set_state(GameState.start)


@dp.message(GameState.start, F.text == "⚔️ Да, вернуть пресс!")
async def start_game(message: types.Message, state: FSMContext):
    await message.answer(
        "Давай сразу уточним. Ты парень или девушка? (м/ж)",
        reply_markup=make_reply_kb(["м", "ж"]),
    )
    await state.set_state(GameState.gender)


@dp.message(GameState.gender, F.text.in_(["м", "ж"]))
async def process_gender(message: types.Message, state: FSMContext):
    gender = message.text.lower()
    await state.update_data(gender=gender)
    if gender == "ж":
        await message.answer(
            "Отлично! Но в Фитосфере все герои — накачанные мужики с щетиной. "
            "Твой аватар будет похож на Стёпу, но не переживай: бицепс не имеет пола. Продолжим!"
        )
    else:
        await message.answer("Отлично! Ты парень — твой аватар будет брутальным.")
    await message.answer("Сколько тебе лет? Только честно, я не налоговая :)")
    await state.set_state(GameState.age)


@dp.message(GameState.age)
async def process_age(message: types.Message, state: FSMContext):
    if not message.text.isdigit() or not (14 <= int(message.text) <= 100):
        await message.answer("🚫 Введи реальный возраст (14-100)")
        return
    await state.update_data(age=int(message.text))
    await message.answer("Рост и вес через пробел, бро. Например: 180 80")
    # Пока останавливаемся тут — базовая проверка, что вебхук жив.
    await state.clear()


# Фолбэк, чтобы было видно в логах, что апдейт долетел,
# даже если ни один FSM-хендлер не сматчился.
@dp.message()
async def fallback(message: types.Message):
    logger.info("Fallback got: %r", message.text)
    await message.answer("Напиши /start, чтобы начать заново.")


# ---------- Webhook lifecycle ----------
async def on_startup(app: web.Application) -> None:
    # drop_pending_updates=True важно, если до этого крутился polling
    # или копились апдейты, пока сервис лежал.
    await bot.set_webhook(
        url=WEBHOOK_URL,
        secret_token=WEBHOOK_SECRET,
        drop_pending_updates=True,
        allowed_updates=dp.resolve_used_update_types(),
    )
    info = await bot.get_webhook_info()
    logger.info("Webhook set to: %s", WEBHOOK_URL)
    logger.info("Webhook info: %s", info)


async def on_shutdown(app: web.Application) -> None:
    logger.info("Shutting down, deleting webhook...")
    await bot.delete_webhook(drop_pending_updates=False)
    await bot.session.close()


async def health(_request: web.Request) -> web.Response:
    return web.Response(text="ok")


def build_app() -> web.Application:
    app = web.Application()
    app.router.add_get("/", health)        # чтобы Render видел, что порт открыт
    app.router.add_get("/health", health)

    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET,
    ).register(app, path=WEBHOOK_PATH)

    setup_application(app, dp, bot=bot)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    return app


def main() -> None:
    logger.info("Starting on port %d, webhook %s", PORT, WEBHOOK_URL)
    web.run_app(build_app(), host="0.0.0.0", port=PORT)


if __name__ == "__main__":
    main()

