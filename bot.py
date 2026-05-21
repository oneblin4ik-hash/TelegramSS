import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

BOT_TOKEN = "8950032855:AAF3puz71ztCKrXMJEdgq8je9K8Cjr7EhOg"

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class GameState(StatesGroup):
    start = State()
    gender = State()
    age = State()

def make_reply_kb(buttons: list[str]) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for b in buttons:
        builder.add(KeyboardButton(text=b))
    return builder.as_markup(resize_keyboard=True)

@dp.message(F.text == "/start")
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🔮 *САГА О ПОТЕРЯННОМ ПРЕССЕ* 🔮\n"
        "Добро пожаловать в Фитосферу, странник.\n"
        "Я — магистр Serbolin.\n"
        "Злой колдун Великий Пельменес украл твой пресс и спрятал его в шести землях.\n"
        "Готов отправиться в поход за своими кубиками?",
        reply_markup=make_reply_kb(["⚔️ Да, вернуть пресс!"])
    )
    await state.set_state(GameState.start)

@dp.message(GameState.start, F.text == "⚔️ Да, вернуть пресс!")
async def start_game(message: types.Message, state: FSMContext):
    await message.answer(
        "Давай сразу уточним. Ты парень или девушка? (м/ж)",
        reply_markup=make_reply_kb(["м", "ж"])
    )
    await state.set_state(GameState.gender)

@dp.message(GameState.gender, F.text.in_(["м", "ж"]))
async def process_gender(message: types.Message, state: FSMContext):
    gender = message.text.lower()
    await state.update_data(gender=gender)
    if gender == "ж":
        await message.answer("Отлично! Но в Фитосфере все герои — накачанные мужики с щетиной. Твой аватар будет похож на Стёпу, но не переживай: бицепс не имеет пола. Продолжим!")
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
    # Пока остановимся тут, чтобы убедиться, что всё работает
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
