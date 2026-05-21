import asyncio
import logging
import os
import sys
import traceback
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

# ---------- Состояния игры ----------
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

# ---------- Изображения ----------
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

# ---------- Вспомогательные функции ----------
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
    """Отправка сообщения с картинкой (если есть) или без."""
    if step_id in IMAGES:
        try:
            await message.answer_photo(photo=IMAGES[step_id], caption=text, reply_markup=reply_markup)
        except Exception as e:
            logging.error(f"Не удалось отправить картинку {step_id}: {e}")
            await message.answer(text, reply_markup=reply_markup)
    else:
        await message.answer(text, reply_markup=reply_markup)

async def send_guide(message: types.Message, filename: str, caption: str = "🎁 Твой гайд:"):
    """Отправка PDF-файла из папки guides/."""
    path = os.path.join(GUIDES_DIR, filename)
    if os.path.exists(path):
        try:
            await message.answer_document(FSInputFile(path), caption=caption)
        except Exception as e:
            logging.error(f"Ошибка отправки гайда {filename}: {e}")
            await message.answer("Гайд временно недоступен, но ты можешь запросить его позже.")
    else:
        await message.answer("Гайд готовится к загрузке. Он появится здесь в ближайшее время.")

async def is_subscribed(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ("member", "administrator", "creator")
    except Exception:
        return False

# ---------- Обработчики ----------
@dp.message(F.text == "/start")
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await send_step(message, "intro",
        "🔮 *САГА О ПОТЕРЯННОМ ПРЕССЕ* 🔮\n"
        "Добро пожаловать в Фитосферу, странник.\n"
        "Я — магистр Serbolin.\n"
        "Злой колдун Великий Пельменес украл твой пресс и спрятал его в шести землях.\n"
        "Готов отправиться в поход за своими кубиками?",
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
        "🔐 *ВРАТА В ФИТОСФЕРУ* 🔐\n"
        "Прежде чем ступить в эти земли, ты должен вступить в элитную гильдию магистра Serbolin’а.\n"
        "Это закрытый клуб для тех, кто реально хочет вернуть свой пресс.\n"
        "Подпишись на канал 👇 и тогда врата откроются.",
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

@dp.callback_query(F.data == "warmup_no")
async def warmup_no(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    score = data.get("score", 50) - 5
    mistakes = data.get("mistakes", []) + ["нет разминки"]
    await state.update_data(score=score, mistakes=mistakes)
    await callback.message.answer("Стёпа: 'Тогда готовься к травме, олух!'")
    await send_step(callback.message, "gym_q2",
        "Вдруг из ниоткуда появляется Арнольдыч, поправляя майку «Pumping Iron». 'Стёпа опять забыл главное правило: тренировки до отказа — не всегда хорошо. Больше — не значит лучше. Прогресс нужно отслеживать, юноша. Дарю тебе дневник тренировок. С ним ты не потеряешь ни одного повторения'.",
        reply_markup=inline_kb([("📓 ВАУ! Забрать дневник", "take_diary")]))
    await state.set_state(GameState.gym_q2)

@dp.callback_query(F.data == "to_gym_q2")
async def to_gym_q2(callback: types.CallbackQuery, state: FSMContext):
    await send_step(callback.message, "gym_q2",
        "Вдруг из ниоткуда появляется Арнольдыч, поправляя майку «Pumping Iron». 'Стёпа опять забыл главное правило: тренировки до отказа — не всегда хорошо. Больше — не значит лучше. Прогресс нужно отслеживать, юноша. Дарю тебе дневник тренировок. С ним ты не потеряешь ни одного повторения'.",
        reply_markup=inline_kb([("📓 ВАУ! Забрать дневник", "take_diary")]))
    await state.set_state(GameState.gym_q2)

@dp.callback_query(F.data == "take_diary")
async def take_diary(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    inventory = data.get("inventory", []) + ["Чек-лист «Как вести дневник тренировок»"]
    await state.update_data(inventory=inventory)
    await callback.message.answer("Арнольдыч исчезает, оставив тебе магический чек-лист.")
    await send_guide(callback.message, "dnevnik.pdf", "Твой чек-лист дневника тренировок")
    await send_step(callback.message, "gym_q3",
        "Арнольдыч (его голос всё ещё звучит): 'Сколько раз в неделю мучаешь железо?'",
        reply_markup=inline_kb([
            ("2-3 раза (мудрый ритм)", "freq_2_3"),
            ("4-5 раз (иногда с трудом)", "freq_4_5"),
            ("6-7 раз, я неудержим!", "freq_6_7")
        ]))
    await state.set_state(GameState.gym_q3)

@dp.callback_query(F.data.startswith("freq_"))
async def process_freq(callback: types.CallbackQuery, state: FSMContext):
    freq = callback.data
    data = await state.get_data()
    score = data.get("score", 50)
    mistakes = data.get("mistakes", [])
    if freq == "freq_2_3":
        score += 10
        comment = "Арнольдыч: 'Ты познал баланс.'"
    elif freq == "freq_4_5":
        score += 5
        comment = "Арнольдыч: 'Не переусердствуй.'"
    else:
        score -= 5
        mistakes.append("перетрен")
        comment = "Где-то вдалеке Стёпа одобрительно свистит."
    await state.update_data(score=score, mistakes=mistakes)
    await callback.message.answer(comment)
    await send_step(callback.message, "gym_q4",
        "Арнольдыч хвалит твой выбор и даёт мудрое наставление: «Готовься слушать тело, а не гнуть его через силу».",
        reply_markup=inline_kb([("🧓 Принимаю мудрость", "accept_wisdom")]))
    await state.set_state(GameState.gym_q4)

@dp.callback_query(F.data == "accept_wisdom")
async def accept_wisdom(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    progress = data.get("progress", 0) + 20
    await state.update_data(progress=progress)
    await callback.message.answer(
        "Ты покидаешь Стальной Храм, мышцы гудят после мудрых советов Арнольдыча. В животе заурчало – видимо, Фитосфера намекает, что пора подкрепиться. Ты отправляешься на поиски Кухни Изобилия. Говорят, там заправляет особа, которая даже брокколи превращает в искусство.",
        reply_markup=inline_kb([("🍲 Вперёд, к холодильнику!", "to_kitchen")]))
    await state.set_state(GameState.to_kitchen)

@dp.callback_query(F.data == "to_kitchen")
async def to_kitchen(callback: types.CallbackQuery, state: FSMContext):
    await send_step(callback.message, "kitchen_intro",
        "🍲 Ты попадаешь на Кухню Изобилия. Жрица Афродита Нутрициевна приветствует тебя: 'Правильное питание — основа силы. Без него даже Стёпа был бы дрищом. Сейчас я тебе кое-что покажу...'",
        reply_markup=inline_kb([("🥗 Слушаю, наставница", "listen_afrodita")]))
    await state.set_state(GameState.kitchen_intro)

@dp.callback_query(F.data == "listen_afrodita")
async def listen_afrodita(callback: types.CallbackQuery, state: FSMContext):
    await send_step(callback.message, "kitchen_q2",
        "Вдруг из портала выплывает поднос с пирожками. Бабушка Пирожкова: 'Внучек, угощайся! С пылу с жару!'",
        reply_markup=inline_kb([
            ("🥧 Спасибо, бабуль, но я на задании.", "reject_pie"),
            ("😋 Один пирожок не помешает.", "accept_pie")
        ]))
    await state.set_state(GameState.kitchen_q2)

@dp.callback_query(F.data.in_(["reject_pie", "accept_pie"]))
async def process_pie(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    score = data.get("score", 50)
    if callback.data == "reject_pie":
        score += 10
        await state.update_data(score=score)
        await callback.message.answer("Бабушка улыбается: 'Ну, смотри, богатырь.'")
    else:
        await callback.message.answer("Афродита: 'Иногда можно, если в меру. Не ругаю.'")
    await send_step(callback.message, "kitchen_q3",
        "Афродита: 'Ты калории считаешь или интуитивно жрёшь?'",
        reply_markup=inline_kb([
            ("📊 Считаю, без фанатизма.", "count_yes"),
            ("🤷 Ем по голоду.", "count_no")
        ]))
    await state.set_state(GameState.kitchen_q3)

@dp.callback_query(F.data.in_(["count_yes", "count_no"]))
async def process_count(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    score = data.get("score", 50)
    mistakes = data.get("mistakes", [])
    if callback.data == "count_yes":
        score += 10
        comment = "Афродита: 'Умничка.'"
    else:
        score -= 5
        mistakes.append("нет контроля порций")
        comment = "Афродита: 'Тогда легко сбиться.'"
    await state.update_data(score=score, mistakes=mistakes)
    await callback.message.answer(comment)
    await send_step(callback.message, "kitchen_q4",
        "Афродита протягивает тебе свиток: 'Вот, держи. Это гайд «Как легко считать КБЖУ». С ним ты не запутаешься в цифрах и не скатишься в РПП.'",
        reply_markup=inline_kb([("📜 Взять свиток", "take_kbju_guide")]))
    await state.set_state(GameState.kitchen_q4)

@dp.callback_query(F.data == "take_kbju_guide")
async def take_kbju_guide(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    inventory = data.get("inventory", []) + ["Гайд «Как легко считать КБЖУ»"]
    await state.update_data(inventory=inventory)
    await callback.message.answer("Свиток занимает место в твоём инвентаре.")
    await send_guide(callback.message, "kbju.pdf", "Твой гайд по КБЖУ")
    await send_step(callback.message, "kitchen_q5",
        "Появляется Смузибой: 'Чё по перекусам – фрукты или шоколад?'",
        reply_markup=inline_kb([
            ("🥜 Орехи/фрукты", "snack_healthy"),
            ("🍫 Шоколадка", "snack_choco"),
            ("⏳ Ничего, голодаю", "snack_starve")
        ]))
    await state.set_state(GameState.kitchen_q5)

@dp.callback_query(F.data.startswith("snack_"))
async def process_snack(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    score = data.get("score", 50)
    mistakes = data.get("mistakes", [])
    if callback.data == "snack_healthy":
        score += 10
        comment = "Смузибой одобряет."
    elif callback.data == "snack_choco":
        score -= 5
        mistakes.append("сладкое")
        comment = "Смузибой: 'Это опасный путь!'"
    else:
        score -= 5
        mistakes.append("голод")
        comment = "Смузибой в ужасе."
    progress = data.get("progress", 0) + 20
    await state.update_data(score=score, mistakes=mistakes, progress=progress)
    await callback.message.answer(comment)
    await callback.message.answer(
        "Ты выходишь с кухни, сытый знаниями (и, возможно, одним пирожком). Но впереди тёмный лес – Лес Искушений, где обитают хейтеры-дрищи. Они чуют неуверенность за километр. Ну что, проверим твою психику на прочность?",
        reply_markup=inline_kb([("🌳 Погнали в дебри!", "to_forest")]))
    await state.set_state(GameState.to_forest)

@dp.callback_query(F.data == "to_forest")
async def to_forest(callback: types.CallbackQuery, state: FSMContext):
    await send_step(callback.message, "brain_meet",
        "🌳 Лес Искушений. Трое хейтеров-дрищей выскакивают из кустов и начинают угарать: 'Смотрите, очередной мечтатель! Думает, что у него будут кубики!'",
        reply_markup=inline_kb([
            ("😠 Терпеть насмешки", "endure"),
            ("💅 Плевать что говорят крысы, за спиной у кисы!", "ignore")
        ]))
    await state.set_state(GameState.brain_meet)

@dp.callback_query(F.data.in_(["endure", "ignore"]))
async def process_meet(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Хейтеры-дрищи: 'Ну и чё ты будешь делать, если через 2 месяца прогресса нет?'",
        reply_markup=inline_kb([
            ("🧠 Поменяю стратегию и продолжу.", "strategy_change"),
            ("🏳️ Брошу всё и сдамся как жалкая сучка", "give_up")
        ]))
    await state.set_state(GameState.brain_question)

@dp.callback_query(F.data.in_(["strategy_change", "give_up"]))
async def process_question(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    score = data.get("score", 50)
    mistakes = data.get("mistakes", [])
    if callback.data == "strategy_change":
        score += 10
        inventory = data.get("inventory", []) + ["Мотивационный гайд: как начать, если нет мотивации"]
        await state.update_data(score=score, inventory=inventory)
        await send_step(callback.message, "brain_question_gift",
            "Гремлины замирают с открытыми ртами, а из воздуха материализуется магистр Serbolin. «Явился, чтобы засвидетельствовать: ты выбрал путь воина. Мотивация приходит и уходит, а система – вечна. Прими этот свиток «Мотивационный гайд: как начать, если нет мотивации»». Он протягивает тебе свиток, переливающийся упрямством.",
            reply_markup=inline_kb([("⚡ Только вперёд!", "after_motivation")]))
        await send_guide(callback.message, "motivation.pdf", "Твой мотивационный гайд")
        await state.set_state(GameState.brain_question_gift)
    else:
        score -= 5
        mistakes.append("короткая дистанция")
        await state.update_data(score=score, mistakes=mistakes)
        await callback.message.answer("Хейтеры-дрищи хихикают.")
        await callback.message.answer(
            "Попугай Кеша орёт в ухо: 'ТЫ СМОЖЕШЬ! ТОПИ КАК ЦАРЬ!'",
            reply_markup=inline_kb([("👑 Я СМОГУ! ТОПИТЬ КАК ЦАРЬ!", "parrot_go")]))
        await state.set_state(GameState.brain_q2)

@dp.callback_query(F.data == "after_motivation")
async def after_motivation(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Попугай Кеша орёт в ухо: 'ТЫ СМОЖЕШЬ! ТОПИ КАК ЦАРЬ!'",
        reply_markup=inline_kb([("👑 Я СМОГУ! ТОПИТЬ КАК ЦАРЬ!", "parrot_go")]))
    await state.set_state(GameState.brain_q2)

@dp.callback_query(F.data == "parrot_go")
async def parrot_go(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Хейтеры-дрищи не унимаются: 'А если нет настроения тренить?'",
        reply_markup=inline_kb([
            ("⚔️ Дисциплина > настроение.", "discipline"),
            ("🎥 Посмотрю мотивационные видео", "motivation_video")
        ]))
    await state.set_state(GameState.brain_q3)

@dp.callback_query(F.data.in_(["discipline", "motivation_video"]))
async def process_brain_q3(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    score = data.get("score", 50)
    mistakes = data.get("mistakes", [])
    if callback.data == "discipline":
        score += 10
        comment = "Serbolin одобрительно кивает."
    else:
        score -= 5
        mistakes.append("нестабильность")
        comment = "Хейтеры-дрищи: 'Ну-ну, надолго ли?'"
    progress = data.get("progress", 0) + 20
    await state.update_data(score=score, mistakes=mistakes, progress=progress)
    await callback.message.answer(comment)
    await callback.message.answer(
        "Ты выбрался из Леса, отбившись от хейтеров-дрищей и попугая-мотиватора. Теперь тебя ждёт Болото Усталости – здесь даже воздух вязкий, а из тумана доносится шёпот: «Приляг… отдохни…». Берегись чар Дивана!",
        reply_markup=inline_kb([("💤 Не поддамся сну!", "to_swamp")]))
    await state.set_state(GameState.to_swamp)

@dp.callback_query(F.data == "to_swamp")
async def to_swamp(callback: types.CallbackQuery, state: FSMContext):
    await send_step(callback.message, "sleep_story",
        "💤 Тебе снится сон. Ты стоишь на распутье: дорога борьбы с ленью или путь деградации на диване. Что выберешь?",
        reply_markup=inline_kb([
            ("⚡ Бороться с ленью!", "fight_lazy"),
            ("🛌 Деградировать...", "degrade")
        ]))
    await state.set_state(GameState.sleep_story)

@dp.callback_query(F.data.in_(["fight_lazy", "degrade"]))
async def process_sleep(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    score = data.get("score", 50)
    mistakes = data.get("mistakes", [])
    if callback.data == "fight_lazy":
        score += 10
        inventory = data.get("inventory", []) + ["Анти-Отек: 5-дневный экспресс-план"]
        await state.update_data(score=score, inventory=inventory)
        await send_step(callback.message, "sleep_story2",
            "Ты делаешь выбор в пользу борьбы с ленью! Диван обиженно скрипит и исчезает, а на его месте возникает Старый Магистр. «За мудрость и бодрость духа прими «Анти-Отек: 5-дневный экспресс-план». Пусть твоё тело будет лёгким, как пёрышко!» Ты получаешь свиток, пахнущий мятой и лимоном.",
            reply_markup=inline_kb([("💧 Спасибо, магистр!", "after_sleep_gift")]))
        await send_guide(callback.message, "anti_otek.pdf", "Твой гайд «Анти-Отек»")
        await state.set_state(GameState.sleep_story2_good)
    else:
        score -= 5
        mistakes.append("лень")
        await state.update_data(score=score, mistakes=mistakes)
        await callback.message.answer(
            "Ты решил деградировать. Диван радостно урчит и обволакивает тебя пушистым пледом. Ты проспал свой прогресс, но, возможно, ещё не всё потеряно.",
            reply_markup=inline_kb([("🛌 Ладно, просыпаюсь...", "wake_up")]))
        await state.set_state(GameState.sleep_story2_bad)

@dp.callback_query(F.data.in_(["after_sleep_gift", "wake_up"]))
async def after_sleep_gift(callback: types.CallbackQuery, state: FSMContext):
    await send_step(callback.message, "sleep_q2",
        "⏰ Звенит Будильник-Страж: 'Вставай, воин! Зарядка или ещё 5 минуточек?'",
        reply_markup=inline_kb([
            ("🛌 Встать и сделать зарядку", "do_exercise"),
            ("😴 Поспать ещё 5 минуточек", "sleep_more")
        ]))
    await state.set_state(GameState.sleep_q2)

@dp.callback_query(F.data.in_(["do_exercise", "sleep_more"]))
async def process_q2(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    score = data.get("score", 50)
    mistakes = data.get("mistakes", [])
    if callback.data == "do_exercise":
        score += 10
        comment = "Будильник довольно звенит."
    else:
        score -= 5
        mistakes.append("пропуск зарядки")
        comment = "Будильник гневается, но даёт тебе ещё шанс."
    await state.update_data(score=score, mistakes=mistakes)
    await callback.message.answer(comment)
    await send_step(callback.message, "sleep_q3",
        "Ты делаешь растяжку. Тело наполняется силой. Болото Усталости позади!",
        reply_markup=inline_kb([("🏃 Двигаться дальше", "go_reallife")]))
    await state.set_state(GameState.sleep_q3)

@dp.callback_query(F.data == "go_reallife")
async def go_reallife(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Ты сделал растяжку и почувствовал прилив сил. Болото осталось позади, а впереди мерцает знакомый офисный свет. Похоже, ты возвращаешься в Реальную Жизнь – туда, где дедлайны, пробки и коллеги с пивом.",
        reply_markup=inline_kb([("🏢 О нет, опять на работу!", "start_real")]))
    await state.set_state(GameState.to_reallife)

@dp.callback_query(F.data == "start_real")
async def start_real(callback: types.CallbackQuery, state: FSMContext):
    await send_step(callback.message, "real_life_story",
        "🏢 Мир людей: аврал, дедлайн, пробки-монстры. Как сохранишь тренировку?",
        reply_markup=inline_kb([
            ("📅 Перенесу, но не пропущу", "real_reschedule"),
            ("❌ Пропущу, не до этого", "real_skip"),
            ("🏠 Сделаю короткую дома", "real_home")
        ]))
    await state.set_state(GameState.real_life_story)

@dp.callback_query(F.data.startswith("real_"))
async def process_real_life(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    score = data.get("score", 50)
    mistakes = data.get("mistakes", [])
    if callback.data == "real_reschedule":
        score += 10
        comment = "Serbolin: 'Системный воин.'"
    elif callback.data == "real_skip":
        score -= 5
        mistakes.append("нестабильность")
        comment = "Serbolin: 'И пресс снова потеряется.'"
    else:
        score += 5
        comment = "Лучше, чем ничего."
    await state.update_data(score=score, mistakes=mistakes)
    await callback.message.answer(comment)
    await send_step(callback.message, "real_life_q2",
        "Коллега зовёт в бар: 'По пиву после дедлайна?'",
        reply_markup=inline_kb([
            ("🍵 Спасибо, у меня тренировка.", "beer_no"),
            ("🍺 Одно пиво не повредит.", "beer_yes")
        ]))
    await state.set_state(GameState.real_life_q2)

@dp.callback_query(F.data.in_(["beer_no", "beer_yes"]))
async def process_beer(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if callback.data == "beer_no":
        score = data.get("score", 50) + 10
        await state.update_data(score=score)
        await callback.message.answer("Коллега уважает.")
    await send_step(callback.message, "real_life_q3",
        "Магический дневник пищит: 'Приём пищи пропущен!'",
        reply_markup=inline_kb([
            ("🥗 Контейнер с готовой едой", "food_container"),
            ("🍔 Заказать бургер", "food_burger")
        ]))
    await state.set_state(GameState.real_life_q3)

@dp.callback_query(F.data.in_(["food_container", "food_burger"]))
async def process_food(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    score = data.get("score", 50)
    mistakes = data.get("mistakes", [])
    if callback.data == "food_container":
        score += 10
        comment = "Дневник сияет зелёным."
    else:
        score -= 5
        mistakes.append("фастфуд")
        comment = "Дневник краснеет."
    await state.update_data(score=score, mistakes=mistakes)
    await callback.message.answer(comment)
    await callback.message.answer(
        "Ты справляешься с офисными соблазнами, но чувствуешь, что один из врагов всё ещё силён. Пришло время назвать его имя.",
        reply_markup=inline_kb([("😤 Назову врага!", "name_enemy")]))
    await state.set_state(GameState.to_reallife_q4)

@dp.callback_query(F.data == "name_enemy")
async def name_enemy(callback: types.CallbackQuery, state: FSMContext):
    await send_step(callback.message, "real_life_q4",
        "Назови главного врага, который ещё крадёт твой пресс:",
        reply_markup=inline_kb([
            ("🌙 Вечерний жор", "enemy_night"),
            ("🍬 Сладкое", "enemy_sweet"),
            ("⏭️ Пропуск еды", "enemy_skip")
        ]))
    await state.set_state(GameState.real_life_q4)

@dp.callback_query(F.data.startswith("enemy_"))
async def process_enemy(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    mistakes = data.get("mistakes", [])
    if callback.data == "enemy_night":
        mistakes.append("вечерний жор")
        comment = "Пельменес облизнулся."
    elif callback.data == "enemy_sweet":
        mistakes.append("сладкое")
        comment = "Печеньки атакуют."
    else:
        mistakes.append("голод")
        comment = "Метаболизм страдает."
    progress = data.get("progress", 0) + 20
    await state.update_data(mistakes=mistakes, progress=progress)
    await callback.message.answer(comment)
    await callback.message.answer(
        "Ты расправился с офисными драконами и почувствовал, что главный враг где-то рядом. Запах теста и сметаны приводит тебя к воротам из слоёного теста. Это Царство Пельменеса – обитель Великого Переедания. Пора сразиться с боссом!",
        reply_markup=inline_kb([("🥟 В логово пельменя!", "to_boss")]))
    await state.set_state(GameState.to_boss)

@dp.callback_query(F.data == "to_boss")
async def to_boss(callback: types.CallbackQuery, state: FSMContext):
    await send_step(callback.message, "boss_intro",
        "🥟 *ЦАРСТВО ПЕЛЬМЕНЕСА* 🥟\n"
        "На огромном блюде восседает Великий Пельменес — гигантский пельмень с короной из теста, глазами-маслинами и сметанной мантией.\n"
        "'Я — повелитель переедания! Твой пресс у меня в начинке! Ответишь на мой вопрос — получишь его обратно!'",
        reply_markup=inline_kb([("⚔️ Задать вопрос", "boss_question")]))
    await state.set_state(GameState.boss_intro)

@dp.callback_query(F.data == "boss_question")
async def boss_question(callback: types.CallbackQuery, state: FSMContext):
    await send_step(callback.message, "boss_riddle",
        "Великий Пельменес ревёт:\n"
        "'Как правильно обращаться с вкусной, но вредной едой?'",
        reply_markup=inline_kb([
            ("🥟 Есть осознанно, иногда, не запрещая себе", "boss_balance"),
            ("🚫 Полностью запретить всё вкусное", "boss_ban"),
            ("🍽 Есть всё подряд, жизнь одна", "boss_all")
        ]))
    await state.set_state(GameState.boss_riddle)

@dp.callback_query(F.data.startswith("boss_"))
async def process_boss(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    score = data.get("score", 50)
    mistakes = data.get("mistakes", [])
    inventory = data.get("inventory", [])
    if callback.data == "boss_balance":
        score += 20
        inventory.append("Укротитель пельменей")
        comment = "Пельменес лопается! Ты получаешь свой пресс!"
    elif callback.data == "boss_ban":
        score -= 10
        mistakes.append("запреты")
        comment = "Пельменес смеётся: 'Слабо!'"
    else:
        score -= 10
        mistakes.append("вседозволенность")
        comment = "Пельменес хохочет: 'Ты в моей власти!'"
    await state.update_data(score=score, mistakes=mistakes, inventory=inventory)
    await callback.message.answer(comment)
    await send_step(callback.message, "boss_victory",
        "🎉 Пельменес повержен! Из его недр вылетает последний фрагмент твоего пресса.\n"
        "'Ладно, ты победил... угости хоть сметанкой напоследок.'",
        reply_markup=inline_kb([("🥄 Угостить сметанкой", "boss_final")]))
    await state.set_state(GameState.boss_victory)

@dp.callback_query(F.data == "boss_final")
async def boss_final(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    score = data.get("score", 50)
    goal = data.get("goal", "")
    mistakes = data.get("mistakes", [])
    inventory = data.get("inventory", [])
    w = data.get("weight", 80)
    h = data.get("height", 175)
    age = data.get("age", 30)
    gender = data.get("gender", "м")

    inv_list = "\n".join(f"• {i}" for i in inventory) if inventory else "Ничего не собрано"
    err_list = "\n".join(f"• {e}" for e in mistakes) if mistakes else "Ты прошёл идеально!"

    bmr = (10*w + 6.25*h - 5*age + 5) if gender == "м" else (10*w + 6.25*h - 5*age - 161)
    tdee = round(bmr * 1.55)
    if goal == "сжечь жир":
        target_cal = round(tdee * 0.85)
    elif goal == "набрать массу":
        target_cal = round(tdee * 1.1)
    else:
        target_cal = tdee
    protein = round(w * 1.6)
    fat = round(w * 0.9)
    carb = round((target_cal - protein*4 - fat*9) / 4)

    personal = f"🎯 *Твоя миссия:* {goal}\n"
    if goal == "сжечь жир":
        personal += "Без дефицита калорий жир не уйдет. Ты уже получил гайд по КБЖУ — он поможет.\n"
    elif goal == "набрать массу":
        personal += "Тебе нужен профицит и упор на белок.\n"
    else:
        personal += "Держи баланс в питании и тренировках.\n"
    personal += f"📊 *Нормы КБЖУ:* {target_cal} ккал, Б: {protein} г, Ж: {fat} г, У: {carb} г\n\n"
    personal += "⚠️ *Твои слабые места:*\n"
    if "вечерний жор" in mistakes:
        personal += "• Вечерний жор — убийца дефицита. В «13 советах» есть техника читмила.\n"
    if "нет записей" in mistakes:
        personal += "• Без дневника ты не видишь прогресс. Используй чек-лист.\n"
    if "нестабильность" in mistakes:
        personal += "• Пропуски тренировок — главный враг. Мотивационный гайд поможет.\n"
    if not mistakes:
        personal += "• Ты держишься отлично, продолжай!\n"

    msg = (f"🎉 *САГА ЗАВЕРШЕНА!* 🎉\n\n"
           f"⚡ Очки дисциплины: {score}/100\n"
           f"🐉 Побеждённые враги:\n{err_list}\n\n"
           f"📜 Добытые свитки:\n{inv_list}\n\n"
           f"{personal}\n"
           f"💎 Бесплатная консультация (цена 5-10 тыс.₽) — твоя награда!\n"
           f"Жми кнопку ниже, чтобы оставить заявку.")
    await send_step(callback.message, "diagnostics", msg,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎯 Оставить заявку на консультацию (БЕСПЛАТНО)", callback_data="offer")]
        ]))
    await state.set_state(GameState.diagnostics)

@dp.callback_query(F.data == "offer")
async def offer(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Отправь свой номер телефона (или ник в Telegram), чтобы я мог связаться с тобой для консультации.",
        reply_markup=make_reply_kb(["📱 Отправить контакт"]))
    await state.set_state(GameState.contact)

@dp.message(GameState.contact, F.contact | F.text)
async def process_contact(message: types.Message, state: FSMContext):
    contact = message.contact.phone_number if message.contact else message.text
    data = await state.get_data()
    user = message.from_user
    user_info = f"Имя: {user.full_name}\nUsername: @{user.username}\nКонтакт: {contact}"
    game_info = f"Цель: {data.get('goal')}\nОшибки: {', '.join(data.get('mistakes', []))}\nГайды: {', '.join(data.get('inventory', []))}"
    await bot.send_message(OWNER_ID,
        f"🔥 *Новая заявка на консультацию!*\n\n{user_info}\n\n{game_info}")
    await message.answer("Спасибо! Я скоро свяжусь с тобой. А пока — держи свои свитки и помни: дисциплина решает!",
        reply_markup=types.ReplyKeyboardRemove())
    await state.clear()

# ---------- Запуск вебхука ----------
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
