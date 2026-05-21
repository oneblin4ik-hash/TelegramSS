import asyncio
import logging
import os
import sys
from contextlib import suppress

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
    gym_entrance = State()
    gym_story = State()
    gym_story_gift = State()
    gym_q2 = State()
    gym_q3 = State()
    gym_q4 = State()
    to_kitchen = State()
    kitchen_intro = State()
    kitchen_q2 = State()
    kitchen_q3 = State()
    kitchen_q4 = State()
    kitchen_q5 = State()
    to_forest = State()
    brain_meet = State()
    brain_question = State()
    brain_question_gift = State()
    brain_q2 = State()
    brain_q3 = State()
    to_swamp = State()
    sleep_story = State()
    sleep_story2_good = State()
    sleep_story2_bad = State()
    sleep_q2 = State()
    sleep_q3 = State()
    to_reallife = State()
    real_life_story = State()
    real_life_q2 = State()
    real_life_q3 = State()
    to_reallife_q4 = State()
    real_life_q4 = State()
    to_boss = State()
    boss_intro = State()
    boss_riddle = State()
    boss_victory = State()
    diagnostics = State()
    offer = State()
    contact = State()

IMAGES = {
    "intro": "https://i.imgur.com/66HuAKT.png",
    "gender": "https://i.imgur.com/RO1jfli.jpeg",
    "gender_female_joke": "https://i.imgur.com/uVg5axv.jpeg",
    "age": "https://i.imgur.com/GS8yfiS.jpeg",
    "body": "https://i.imgur.com/pzqvS2z.jpeg?1",
    "goal": "https://i.imgur.com/GUB8fdb.jpeg",
    "guild_intro": "https://i.imgur.com/EqT0hbp.jpeg",
    "guild_check": "https://i.imgur.com/EqT0hbp.jpeg",
    "firstChoice": "https://i.imgur.com/9Nso4Fb.jpeg",
    "gym_entrance": "https://i.imgur.com/QuAi4Wd.jpeg",
    "gym_story": "https://i.imgur.com/k3FFVWr.jpeg",
    "gym_story_gift": "https://i.imgur.com/k3FFVWr.jpeg",
    "gym_q2": "https://i.imgur.com/y3TI8an.jpeg",
    "gym_q3": "https://i.imgur.com/4M1JRvd.jpeg",
    "gym_q4": "https://i.imgur.com/4M1JRvd.jpeg",
    "kitchen_intro": "https://i.imgur.com/oD2G75p.jpeg",
    "kitchen_q2": "https://i.imgur.com/jzv7o1h.jpeg",
    "kitchen_q3": "https://i.imgur.com/A9TOxJz.jpeg",
    "kitchen_q4": "https://i.imgur.com/eo5qObo.png",
    "kitchen_q5": "https://i.imgur.com/ZLXJwjp.jpeg",
    "brain_meet": "https://i.imgur.com/QTrG8jS.jpeg",
    "brain_question_gift": "https://i.imgur.com/hcUrbk0.png",
    "brain_q2": "https://i.imgur.com/JBbTSPJ.jpeg",
    "sleep_story": "https://i.imgur.com/kzen3CE.jpeg",
    "sleep_story2": "https://i.imgur.com/zqFLfG0.jpeg",
    "sleep_q2": "https://i.imgur.com/GvDZAFL.jpeg",
    "sleep_q3": "https://i.imgur.com/kyC1ur0.jpeg",
    "real_life_story": "https://i.imgur.com/CPCpOIt.jpeg",
    "real_life_q2": "https://i.imgur.com/BCxrsMu.jpeg",
    "real_life_q3": "https://i.imgur.com/gZtzmkz.jpeg",
    "real_life_q4": "https://i.imgur.com/C3nkbxo.jpeg",
    "boss_intro": "https://i.imgur.com/a9Wq1l2.jpeg",
    "boss_riddle": "https://i.imgur.com/vqjZvw5.jpeg",
    "boss_victory": "https://i.imgur.com/nJnmg5v.jpeg",
    "diagnostics": "https://i.imgur.com/hxhRZbm.jpeg",
    "offer": "https://i.imgur.com/9HwguXs.jpeg",
    "contact": "https://i.imgur.com/28Jik7b.jpeg",
    "end": "https://i.imgur.com/Sq4MzGe.jpeg",
}

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
    if step_id in IMAGES:
        try:
            await message.answer_photo(photo=IMAGES[step_id], caption=text, reply_markup=reply_markup)
        except Exception:
            await message.answer(text, reply_markup=reply_markup)
    else:
        await message.answer(text, reply_markup=reply_markup)

async def send_guide(message: types.Message, filename: str, caption: str = "🎁 Твой гайд:"):
    path = os.path.join(GUIDES_DIR, filename)
    if os.path.exists(path):
        try:
            await message.answer_document(FSInputFile(path), caption=caption)
        except Exception:
            await message.answer("Гайд временно недоступен, но ты можешь запросить его позже.")
    else:
        await message.answer("Гайд готовится к загрузке. Он появится здесь в ближайшее время.")

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
        await send_step(message, "gender_female_joke",
            "Отлично! Но в Фитосфере все герои — накачанные мужики с щетиной. Твой аватар будет похож на Стёпу, но не переживай: бицепс не имеет пола. Продолжим!")
        await message.answer("Сколько тебе лет? Только честно, я не налоговая :)")
    else:
        await send_step(message, "gender", "Отлично! Ты парень — твой аватар будет брутальным.")
        await message.answer("Сколько тебе лет? Только честно, я не налоговая :)")
    await state.set_state(GameState.age)

@dp.message(GameState.age)
async def process_age(message: types.Message, state: FSMContext):
    if not message.text.isdigit() or not (14 <= int(message.text) <= 100):
        await message.answer("🚫 Введи реальный возраст (14-100)")
        return
    await state.update_data(age=int(message.text))
    await send_step(message, "body", "Рост и вес через пробел, бро. Например: 180 80")
    await state.set_state(GameState.body)

@dp.message(GameState.body)
async def process_body(message: types.Message, state: FSMContext):
    parts = message.text.split()
    if len(parts) != 2 or not all(p.isdigit() for p in parts):
        await message.answer("🚫 Введи два числа через пробел")
        return
    await state.update_data(height=int(parts[0]), weight=int(parts[1]))
    await send_step(message, "goal", "Какая миссия у тебя в Фитосфере?", reply_markup=make_reply_kb([
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
    await send_step(message, "guild_intro",
        "🔐 *ВРАТА В ФИТОСФЕРУ* 🔐\nПрежде чем ступить в эти земли, ты должен вступить в элитную гильдию магистра Serbolin’а.\nЭто закрытый клуб для тех, кто реально хочет вернуть свой пресс.\nПодпишись на канал 👇 и тогда врата откроются.",
        reply_markup=inline_kb([("📢 Подписаться на канал Mr. Serbolin", "go_guild")]))
    await state.set_state(GameState.guild_intro)

@dp.callback_query(F.data == "go_guild")
async def go_guild(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Проверяю подписку...")
    if await is_subscribed(callback.from_user.id):
        await callback.message.answer("Ты в гильдии! Врата открываются...")
        await send_step(callback.message, "firstChoice",
            "Ты стоишь перед вратами Стального Храма. Справа — вход в зал, слева — тропа сомнений, где бродят хейтеры-дрищи.",
            reply_markup=inline_kb([
                ("🏋️ Войти в Храм (встретить Стёпу)", "enter_gym"),
                ("📱 Пойти налево (опасность)", "go_left")
            ]))
        await state.set_state(GameState.first_choice)
    else:
        await callback.message.answer("Ты ещё не в гильдии. Подпишись и возвращайся.",
                                      reply_markup=inline_kb([("📢 Подписаться на канал", "go_guild")]))
    await callback.answer()

@dp.callback_query(F.data == "enter_gym")
async def enter_gym(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    score = data.get("score", 50) + 10
    await state.update_data(score=score)
    await callback.message.answer("Serbolin: 'Хороший выбор. Приготовься к испытаниям.'")
    await send_step(callback.message, "gym_entrance",
        "Ты входишь в Стальной Храм. Перед тобой возвышается огромный Стёпа Железный. 'Ну, новенький, готов к проверке?'",
        reply_markup=inline_kb([("🔥 Готов!", "ready_gym")]))
    await state.set_state(GameState.gym_entrance)

@dp.callback_query(F.data == "ready_gym")
async def ready_gym(callback: types.CallbackQuery, state: FSMContext):
    await send_step(callback.message, "gym_story",
        "💢 Стёпа орёт: 'Без разминки в Храм нельзя! Покажи, что умеешь!'",
        reply_markup=inline_kb([
            ("🔥 Всегда разминаюсь!", "warmup_yes"),
            ("🤷 Да ладно, я так, налегке.", "warmup_no")
        ]))
    await state.set_state(GameState.gym_story)

@dp.callback_query(F.data == "warmup_yes")
async def warmup_yes(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    score = data.get("score", 50) + 10
    inventory = data.get("inventory", []) + ["Гайд «13 советов как всегда быть в форме»"]
    await state.update_data(score=score, inventory=inventory)
    await send_step(callback.message, "gym_story_gift",
        "Стёпа одобрительно ревёт и из-за спины достаёт потрёпанный, но сияющий свиток. «Держи, салага! Это «13 советов как всегда быть в форме» – кодекс выживания в нашем мире. Не потеряй, а то Арнольдыч расстроится». Ты бережно принимаешь свиток, чувствуя, как он нагревается от магии.",
        reply_markup=inline_kb([("📜 Клянусь не терять!", "to_gym_q2")]))
    await send_guide(callback.message, "13_sovetov.pdf", "Твой гайд «13 советов»")
    await state.set_state(GameState.gym_story_gift)

# Продолжение следует...
# (полный код далее аналогичен предыдущему полному варианту, но с улучшенной обработкой изображений)
