import asyncio
import logging
import os
import sys
from aiogram import Bot, Dispatcher, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
    FSInputFile
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

BOT_TOKEN = "8950032855:AAF3puz71ztCKrXMJEdgq8je9K8Cjr7EhOg"
OWNER_ID = 708122486
CHANNEL_ID = -1002095605776
CHANNEL_URL = "https://t.me/Mr_Serbolin"
GUIDES_DIR = "guides"
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL", "https://your-service.onrender.com")

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class GameState(StatesGroup):
    start = State()
    gender = State()
    age = State()
    body = State()
    goal = State()
    guild_intro = State()
    guild_check = State()
    first_choice = State()
    # Пока остановимся здесь, остальные состояния добавим позже

IMAGES = {}  # Пока без картинок, чтобы исключить проблему с URL

def make_reply_kb(buttons: list[str]) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for b in buttons:
        builder.add(KeyboardButton(text=b))
    return builder.as_markup(resize_keyboard=True)

def inline_kb(buttons: list[tuple[str, str]]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for text, callback in buttons:
        builder.button(text=text, callback_data=callback)
    return builder.as_markup()

async def send_step(message: types.Message, step_id: str, text: str, reply_markup=None):
    # Временно без картинок
    await message.answer(text, reply_markup=reply_markup)

async def is_subscribed(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ("member", "administrator", "creator")
    except Exception:
        return False

@dp.message(F.text == "/start")
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await send_step(message, "intro",
        "🔮 *САГА О ПОТЕРЯННОМ ПРЕССЕ* 🔮\nДобро пожаловать в Фитосферу, странник.\nЯ — магистр Serbolin.\nЗлой колдун Великий Пельменес украл твой пресс и спрятал его в шести землях.\nГотов отправиться в поход за своими кубиками?",
        reply_markup=make_reply_kb(["⚔️ Да, вернуть пресс!"]))
    await state.set_state(GameState.start)

@dp.message(GameState.start, F.text == "⚔️ Да, вернуть пресс!")
async def start_game(message: types.Message, state: FSMContext):
    await message.answer("Давай сразу уточним. Ты парень или девушка? (м/ж)", reply_markup=make_reply_kb(["м", "ж"]))
    await state.set_state(GameState.gender)

@dp.message(GameState.gender, F.text.in_(["м", "ж"]))
async def process_gender(message: types.Message, state: FSMContext):
    gender = message.text.lower()
    await state.update_data(gender=gender, score=50, progress=0, mistakes=[], inventory=[])
    if gender == "ж":
        await message.answer("Отлично! Но в Фитосфере все герои — накачанные мужики с щетиной. Твой аватар будет похож на Стёпу, но не переживай: бицепс не имеет пола. Продолжим!")
    await message.answer("Сколько тебе лет? Только честно, я не налоговая :)")
    await state.set_state(GameState.age)

@dp.message(GameState.age)
async def process_age(message: types.Message, state: FSMContext):
    if not message.text.isdigit() or not (14 <= int(message.text) <= 100):
        await message.answer("🚫 Введи реальный возраст (14-100)")
        return
    await state.update_data(age=int(message.text))
    await message.answer("Рост и вес через пробел, бро. Например: 180 80")
    await state.set_state(GameState.body)

@dp.message(GameState.body)
async def process_body(message: types.Message, state: FSMContext):
    parts = message.text.split()
    if len(parts) != 2 or not all(p.isdigit() for p in parts):
        await message.answer("🚫 Введи два числа через пробел")
        return
    await state.update_data(height=int(parts[0]), weight=int(parts[1]))
    await message.answer("Какая миссия у тебя в Фитосфере?", reply_markup=make_reply_kb([
        "🔥 Сжечь жир и явить рельеф",
        "💪 Нарастить мышечную броню",
        "⚡ Обрести энергию и лёгкость"
    ]))
    await state.set_state(GameState.goal)

@dp.message(GameState.goal)
async def process_goal(message: types.Message, state: FSMContext):
    goal_map = {
        "🔥 Сжечь жир и явить рельеф": "сжечь жир",
        "💪 Нарастить мышечную броню": "набрать массу",
        "⚡ Обрести энергию и лёгкость": "энергия"
    }
    goal = goal_map.get(message.text)
    if not goal:
        await message.answer("Выбери одну из миссий кнопками")
        return
    await state.update_data(goal=goal)
    await message.answer("🔐 *ВРАТА В ФИТОСФЕРУ* 🔐\nПрежде чем ступить в эти земли, ты должен вступить в элитную гильдию магистра Serbolin’а.\nЭто закрытый клуб для тех, кто реально хочет вернуть свой пресс.\nПодпишись на канал 👇 и тогда врата откроются.",
        reply_markup=inline_kb([("📢 Подписаться на канал Mr. Serbolin", "go_guild")]))
    await state.set_state(GameState.guild_intro)

@dp.callback_query(F.data == "go_guild")
async def go_guild(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Проверяю подписку...")
    if await is_subscribed(callback.from_user.id):
        await callback.message.answer("Ты в гильдии! Врата открываются...")
        # Пока просто завершаем, дальше добавим остальные уровни
        await callback.message.answer("Продолжение следует... (игра в разработке)")
    else:
        await callback.message.answer("Ты ещё не в гильдии. Подпишись и возвращайся.",
                                      reply_markup=inline_kb([("📢 Подписаться на канал", "go_guild")]))
    await callback.answer()

async def on_startup(bot: Bot):
    webhook_url = f"{RENDER_EXTERNAL_URL}/webhook"
    await bot.set_webhook(webhook_url)
    logging.info(f"Webhook set to {webhook_url}")

async def on_shutdown(bot: Bot):
    await bot.delete_webhook()

async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_requests_handler.register(app, path="/webhook")
    setup_application(app, dp, bot=bot)

    port = int(os.getenv("PORT", 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logging.info(f"Server started on port {port}")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
