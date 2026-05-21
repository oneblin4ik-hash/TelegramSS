"""Saga of the Lost Press — Telegram bot on Vercel serverless.

State is kept in a process-global dict (warm-instance only) with /tmp persistence
as a best-effort fallback. Good enough for an MVP demo.
"""
from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
import urllib.parse
import urllib.error
import traceback

BOT_TOKEN = os.getenv("BOT_TOKEN", "8950032855:AAF3puz71ztCKrXMJEdgq8je9K8Cjr7EhOg")
OWNER_ID = int(os.getenv("OWNER_ID", "708122486"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "-1002095605776"))
CHANNEL_URL = "https://t.me/Mr_Serbolin"
VERCEL_URL = os.getenv("VERCEL_URL", "")  # without protocol
BASE_URL = f"https://{VERCEL_URL}" if VERCEL_URL else ""

# Overridden at runtime from the Host header of the incoming webhook request
_runtime_base_url = ""


def get_base_url():
    return _runtime_base_url or BASE_URL

API = f"https://api.telegram.org/bot{BOT_TOKEN}"

STATE_FILE = "/tmp/saga_states.json"
user_states = {}
try:
    with open(STATE_FILE) as f:
        user_states = json.load(f)
        user_states = {int(k): v for k, v in user_states.items()}
except Exception:
    user_states = {}


def save_states():
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(user_states, f, ensure_ascii=False)
    except Exception as e:
        print(f"save_states error: {e}")


# -------- Telegram API helpers --------

def tg(method, **payload):
    url = f"{API}/{method}"
    data = json.dumps({k: v for k, v in payload.items() if v is not None}).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"TG HTTPError {method}: {e.read().decode()}")
    except Exception as e:
        print(f"TG error {method}: {e}")
    return None


def send_text(chat_id, text, reply_kb=None, inline_kb=None, remove_kb=False):
    rm = None
    if reply_kb:
        rm = {
            "keyboard": [[{"text": b}] for b in reply_kb],
            "resize_keyboard": True,
            "one_time_keyboard": False,
        }
    elif inline_kb:
        rm = {"inline_keyboard": inline_kb}
    elif remove_kb:
        rm = {"remove_keyboard": True}
    return tg("sendMessage", chat_id=chat_id, text=text, reply_markup=rm)


def send_photo(chat_id, photo_url, caption=None):
    return tg("sendPhoto", chat_id=chat_id, photo=photo_url, caption=caption)


def send_document(chat_id, document_url, caption=None):
    return tg("sendDocument", chat_id=chat_id, document=document_url, caption=caption)


def is_subscribed(user_id):
    url = f"{API}/getChatMember?chat_id={CHANNEL_ID}&user_id={user_id}"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read())
            return data.get("result", {}).get("status") in ("member", "administrator", "creator")
    except Exception as e:
        print(f"is_subscribed error: {e}")
        return False


# -------- Images (canonical Imgur URLs, approved by the user) --------

IMAGES = {
    "intro": "https://i.imgur.com/66HuAKT.png",
    "gender": "https://i.imgur.com/RO1jfli.jpeg",
    "gender_female_joke": "https://i.imgur.com/uVg5axv.jpeg",
    "age": "https://i.imgur.com/GS8yfiS.jpeg",
    "body": "https://i.imgur.com/pzqvS2z.jpeg",
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

GUIDE_FILES = {
    "13_sovetov.pdf": "📘 Гайд «13 советов как всегда быть в форме»",
    "dnevnik.pdf": "📓 Чек-лист «Как вести дневник тренировок»",
    "kbju.pdf": "📜 Гайд «Как легко считать КБЖУ»",
    "motivation.pdf": "⚡ Мотивационный гайд: как начать, если нет мотивации",
    "anti_otek.pdf": "💧 Анти-Отек: 5-дневный экспресс-план",
}


# -------- State helpers --------

def get_state(uid):
    s = user_states.get(uid)
    if not s:
        s = {
            "step": "intro_welcome",
            "score": 50,
            "progress": 0,
            "mistakes": [],
            "inventory": [],
            "gender": None, "age": None, "height": None, "weight": None, "goal": None,
        }
        user_states[uid] = s
    return s


def reset_state(uid):
    user_states[uid] = {
        "step": "intro_welcome",
        "score": 50,
        "progress": 0,
        "mistakes": [],
        "inventory": [],
        "gender": None, "age": None, "height": None, "weight": None, "goal": None,
    }
    return user_states[uid]


# -------- Scenario steps --------
# Each step: {image, text, buttons: [(label, [effects], next_step)], input: optional}
# Effects: ("score", +-N), ("progress", +N), ("mistake", "..."), ("inv", "..."),
#          ("guide", "filename.pdf"), ("msg", "text") — extra comment to send

STEPS = {
    "intro_welcome": {
        "image": "intro",
        "text": "🔮 САГА О ПОТЕРЯННОМ ПРЕССЕ 🔮\n\nДобро пожаловать в Фитосферу, странник.\nЯ — магистр Serbolin.\nЗлой колдун Великий Пельменес украл твой пресс и спрятал его в шести землях.\n\nГотов отправиться в поход за своими кубиками?",
        "buttons": [("⚔️ Да, вернуть пресс!", [], "ask_gender")],
    },
    "ask_gender": {
        "image": "gender",
        "text": "Давай сразу уточним. Ты парень или девушка?",
        "buttons": [
            ("м", [("set_gender", "м")], "ask_age"),
            ("ж", [("set_gender", "ж")], "female_joke"),
        ],
    },
    "female_joke": {
        "image": "gender_female_joke",
        "text": "Отлично! Но в Фитосфере все герои — накачанные мужики с щетиной. Твой аватар будет похож на Стёпу, но не переживай: бицепс не имеет пола. Продолжим!",
        "buttons": [("👉 Продолжить", [], "ask_age")],
    },
    "ask_age": {
        "image": "age",
        "text": "Сколько тебе лет? Только честно, я не налоговая 😉\n\n(введи число от 14 до 100)",
        "input": "age",
    },
    "ask_body": {
        "image": "body",
        "text": "Рост и вес через пробел, бро. Например: 180 80",
        "input": "body",
    },
    "ask_goal": {
        "image": "goal",
        "text": "Какая миссия у тебя в Фитосфере?",
        "buttons": [
            ("🔥 Сжечь жир и явить рельеф", [("set_goal", "сжечь жир")], "subscribe_prompt"),
            ("💪 Нарастить мышечную броню", [("set_goal", "набрать массу")], "subscribe_prompt"),
            ("⚡ Обрести энергию и лёгкость", [("set_goal", "энергия")], "subscribe_prompt"),
        ],
    },
    "subscribe_prompt": {
        "image": "guild_intro",
        "text": "🔐 ВРАТА В ФИТОСФЕРУ 🔐\n\nПрежде чем ступить в эти земли, ты должен вступить в элитную гильдию магистра Serbolin'а.\nЭто закрытый клуб для тех, кто реально хочет вернуть свой пресс.\n\nПодпишись на канал 👇 и тогда врата откроются.",
        "inline": [
            [{"text": "📢 Подписаться на канал", "url": CHANNEL_URL}],
            [{"text": "✅ Я подписался, проверь!", "callback_data": "check_sub"}],
        ],
    },

    # ---- Steps 1+ from scenario ----
    "firstChoice": {
        "image": "firstChoice",
        "text": "Ты стоишь перед вратами Стального Храма. Справа — вход в зал, слева — тропа сомнений, где бродят хейтеры-дрищи.",
        "buttons": [
            ("🏋️ Войти в Храм (встретить Стёпу)", [("score", 10)], "gym_entrance"),
            ("📱 Пойти налево (опасность)", [("score", -5), ("msg", "Serbolin: «О нет, там бродят хейтеры-дрищи...»")], "brain_meet"),
        ],
    },
    "gym_entrance": {
        "image": "gym_entrance",
        "text": "Ты входишь в Стальной Храм. Перед тобой возвышается огромный Стёпа Железный.\n«Ну, новенький, готов к проверке?»",
        "buttons": [("🔥 Готов!", [], "gym_story")],
    },
    "gym_story": {
        "image": "gym_story",
        "text": "💢 Стёпа орёт: «Без разминки в Храм нельзя! Покажи, что умеешь!»",
        "buttons": [
            ("🔥 Всегда разминаюсь!", [
                ("score", 10),
                ("inv", "Гайд «13 советов как всегда быть в форме»"),
                ("guide", "13_sovetov.pdf"),
                ("msg", "Стёпа одобрительно кивает: «Вот это по-нашему. Держи свиток мудрости.»"),
            ], "gym_q2"),
            ("🤷 Да ладно, я так, налегке.", [
                ("score", -5),
                ("mistake", "нет разминки"),
                ("msg", "Стёпа хмурится: «Без разминки — прямой путь к травме, юнец.»"),
            ], "gym_q2"),
        ],
    },
    "gym_q2": {
        "image": "gym_q2",
        "text": "Вдруг из ниоткуда появляется Арнольдыч...\n«Стёпа опять забыл главное правило: тренировки до отказа — не всегда хорошо. Больше — не значит лучше. Прогресс нужно отслеживать, юноша. Дарю тебе дневник тренировок. С ним ты не потеряешь ни одного повторения.»",
        "buttons": [("📓 ВАУ! Забрать дневник", [
            ("inv", "Чек-лист «Как вести дневник тренировок»"),
            ("guide", "dnevnik.pdf"),
        ], "gym_q3")],
    },
    "gym_q3": {
        "image": "gym_q3",
        "text": "Арнольдыч (его голос всё ещё звучит):\n«Сколько раз в неделю мучаешь железо?»",
        "buttons": [
            ("2-3 раза (мудрый ритм)", [("score", 10), ("msg", "«Идеально! Восстановление — половина успеха.»")], "gym_q4"),
            ("4-5 раз (иногда с трудом)", [("score", 5), ("msg", "«Достойно, но следи за восстановлением.»")], "gym_q4"),
            ("6-7 раз, я неудержим!", [("score", -5), ("mistake", "перетрен"), ("msg", "«Это путь к перетренированности и плато. Сбавь обороты.»")], "gym_q4"),
        ],
    },
    "gym_q4": {
        "image": "gym_q4",
        "text": "Арнольдыч хвалит твой выбор и даёт мудрое наставление: «Готовься слушать тело, а не гнуть его через силу».",
        "buttons": [("🧓 Принимаю мудрость", [("progress", 20)], "to_kitchen")],
    },
    "to_kitchen": {
        "image": None,
        "text": "Ты покидаешь Стальной Храм... пора подкрепиться. Ты отправляешься на поиски Кухни Изобилия...",
        "buttons": [("🍲 Вперёд, к холодильнику!", [], "kitchen_intro")],
    },
    "kitchen_intro": {
        "image": "kitchen_intro",
        "text": "🍲 Ты попадаешь на Кухню Изобилия. Жрица Афродита Нутрициевна приветствует тебя:\n«Правильное питание — основа силы... Сейчас я тебе кое-что покажу...»",
        "buttons": [("🥗 Слушаю, наставница", [], "kitchen_q2")],
    },
    "kitchen_q2": {
        "image": "kitchen_q2",
        "text": "Вдруг из портала выплывает поднос с пирожками. Бабушка Пирожкова:\n«Внучек, угощайся! С пылу с жару!»",
        "buttons": [
            ("🥧 Спасибо, бабуль, но я на задании.", [("score", 10), ("msg", "Афродита одобрительно улыбается.")], "kitchen_q3"),
            ("😋 Один пирожок не помешает.", [("msg", "Бабушка довольна, Афродита косится — но без штрафа.")], "kitchen_q3"),
        ],
    },
    "kitchen_q3": {
        "image": "kitchen_q3",
        "text": "Афродита: «Ты калории считаешь или интуитивно жрёшь?»",
        "buttons": [
            ("📊 Считаю, без фанатизма.", [("score", 10), ("msg", "«Это путь воина.»")], "kitchen_q4"),
            ("🤷 Ем по голоду.", [("score", -5), ("mistake", "нет контроля порций"), ("msg", "«Голод — не лучший советник, особенно вечером.»")], "kitchen_q4"),
        ],
    },
    "kitchen_q4": {
        "image": "kitchen_q4",
        "text": "Афродита протягивает тебе свиток:\n«Вот, держи. Это гайд „Как легко считать КБЖУ“. С ним ты не запутаешься в цифрах и не скатишься в РПП.»",
        "buttons": [("📜 Взять свиток", [
            ("inv", "Гайд «Как легко считать КБЖУ»"),
            ("guide", "kbju.pdf"),
        ], "kitchen_q5")],
    },
    "kitchen_q5": {
        "image": "kitchen_q5",
        "text": "Появляется Смузибой: «Чё по перекусам — фрукты или шоколад?»",
        "buttons": [
            ("🥜 Орехи/фрукты", [("score", 10), ("msg", "«Топ!»")], "to_forest"),
            ("🍫 Шоколадка", [("score", -5), ("mistake", "сладкое"), ("msg", "«Сахар — главный вор пресса.»")], "to_forest"),
            ("⏳ Ничего, голодаю", [("score", -5), ("mistake", "голод"), ("msg", "«Голодание днём = срыв вечером.»")], "to_forest"),
        ],
    },
    "to_forest": {
        "image": None,
        "text": "Ты выходишь с кухни, сытый знаниями... Но впереди тёмный лес — Лес Искушений, где обитают хейтеры-дрищи...",
        "buttons": [("🌳 Погнали в дебри!", [("progress", 20)], "brain_meet")],
    },
    "brain_meet": {
        "image": "brain_meet",
        "text": "🌳 Лес Искушений. Трое хейтеров-дрищей выскакивают из кустов и начинают угарать:\n«Смотрите, очередной мечтатель! Думает, что у него будут кубики!»",
        "buttons": [
            ("😠 Терпеть насмешки", [], "brain_question"),
            ("💅 Плевать что говорят крысы, за спиной у кисы!", [], "brain_question"),
        ],
    },
    "brain_question": {
        "image": None,
        "text": "Хейтеры-дрищи: «Ну и чё ты будешь делать, если через 2 месяца прогресса нет?»",
        "buttons": [
            ("🧠 Поменяю стратегию и продолжу.", [
                ("score", 10),
                ("inv", "Мотивационный гайд"),
                ("guide", "motivation.pdf"),
            ], "brain_question_gift"),
            ("🏳️ Брошу всё и сдамся как жалкая сучка", [
                ("score", -5),
                ("mistake", "короткая дистанция"),
                ("msg", "Хейтеры довольно ржут. Serbolin вздыхает: «Запомни — дистанция решает всё.»"),
            ], "brain_q2"),
        ],
    },
    "brain_question_gift": {
        "image": "brain_question_gift",
        "text": "Гремлины замирают... магистр Serbolin вручает тебе свиток «Мотивационный гайд».",
        "buttons": [("⚡ Только вперёд!", [], "brain_q2")],
    },
    "brain_q2": {
        "image": "brain_q2",
        "text": "Попугай Кеша орёт в ухо: «ТЫ СМОЖЕШЬ! ТОПИ КАК ЦАРЬ!»",
        "buttons": [("👑 Я СМОГУ! ТОПИТЬ КАК ЦАРЬ!", [], "brain_q3")],
    },
    "brain_q3": {
        "image": None,
        "text": "Хейтеры-дрищи не унимаются: «А если нет настроения тренить?»",
        "buttons": [
            ("⚔️ Дисциплина > настроение.", [("score", 10), ("msg", "«Это ключ к телу мечты.»")], "to_swamp"),
            ("🎥 Посмотрю мотивационные видео", [("score", -5), ("mistake", "нестабильность"), ("msg", "«Мотивация заканчивается, дисциплина — нет.»")], "to_swamp"),
        ],
    },
    "to_swamp": {
        "image": None,
        "text": "Ты выбрался из Леса... Теперь тебя ждёт Болото Усталости...",
        "buttons": [("💤 Не поддамся сну!", [("progress", 20)], "sleep_story")],
    },
    "sleep_story": {
        "image": "sleep_story",
        "text": "💤 Тебе снится сон. Ты стоишь на распутье: дорога борьбы с ленью или путь деградации на диване.\nЧто выберешь?",
        "buttons": [
            ("⚡ Бороться с ленью!", [
                ("score", 10),
                ("inv", "Анти-Отек: 5-дневный экспресс-план"),
                ("guide", "anti_otek.pdf"),
            ], "sleep_story2_good"),
            ("🛌 Деградировать...", [
                ("score", -5),
                ("mistake", "лень"),
            ], "sleep_story2_bad"),
        ],
    },
    "sleep_story2_good": {
        "image": "sleep_story2",
        "text": "Ты делаешь выбор в пользу борьбы с ленью!\nСтарый Магистр вручает тебе «Анти-Отек».",
        "buttons": [("💧 Спасибо, магистр!", [], "sleep_q2")],
    },
    "sleep_story2_bad": {
        "image": "sleep_story2",
        "text": "Ты решил деградировать. Диван радостно урчит...\nТы проспал свой прогресс, но, возможно, ещё не всё потеряно.",
        "buttons": [("🛌 Ладно, просыпаюсь...", [], "sleep_q2")],
    },
    "sleep_q2": {
        "image": "sleep_q2",
        "text": "⏰ Звенит Будильник-Страж: «Вставай, воин! Зарядка или ещё 5 минуточек?»",
        "buttons": [
            ("🛌 Встать и сделать зарядку", [("score", 10), ("msg", "«Лучший старт дня!»")], "sleep_q3"),
            ("😴 Поспать ещё 5 минуточек", [("score", -5), ("mistake", "пропуск зарядки"), ("msg", "«5 минуточек превращаются в час...»")], "sleep_q3"),
        ],
    },
    "sleep_q3": {
        "image": "sleep_q3",
        "text": "Ты делаешь растяжку. Тело наполняется силой. Болото Усталости позади!",
        "buttons": [("🏃 Двигаться дальше", [("progress", 20)], "to_reallife")],
    },
    "to_reallife": {
        "image": None,
        "text": "Ты сделал растяжку... Похоже, ты возвращаешься в Реальную Жизнь...",
        "buttons": [("🏢 О нет, опять на работу!", [], "real_life_story")],
    },
    "real_life_story": {
        "image": "real_life_story",
        "text": "🏢 Мир людей: аврал, дедлайн, пробки-монстры. Как сохранишь тренировку?",
        "buttons": [
            ("📅 Перенесу, но не пропущу", [("score", 10), ("msg", "«Гибкость = выживаемость.»")], "real_life_q2"),
            ("❌ Пропущу, не до этого", [("score", -5), ("mistake", "нестабильность"), ("msg", "«Один пропуск тянет за собой второй.»")], "real_life_q2"),
            ("🏠 Сделаю короткую дома", [("score", 5), ("msg", "«15 минут лучше, чем 0.»")], "real_life_q2"),
        ],
    },
    "real_life_q2": {
        "image": "real_life_q2",
        "text": "Коллега зовёт в бар: «По пиву после дедлайна?»",
        "buttons": [
            ("🍵 Спасибо, у меня тренировка.", [("score", 10), ("msg", "«Воин!»")], "real_life_q3"),
            ("🍺 Одно пиво не повредит.", [("msg", "«Одно превращается в три...»")], "real_life_q3"),
        ],
    },
    "real_life_q3": {
        "image": "real_life_q3",
        "text": "Магический дневник пищит: «Приём пищи пропущен!»",
        "buttons": [
            ("🥗 Контейнер с готовой едой", [("score", 10), ("msg", "«Заготовки спасают жизни и прессы.»")], "to_reallife_q4"),
            ("🍔 Заказать бургер", [("score", -5), ("mistake", "фастфуд"), ("msg", "«Быстро, но дорого — твоим прессом.»")], "to_reallife_q4"),
        ],
    },
    "to_reallife_q4": {
        "image": None,
        "text": "Ты справляешься с офисными соблазнами... Пришло время назвать его имя.",
        "buttons": [("😤 Назову врага!", [], "real_life_q4")],
    },
    "real_life_q4": {
        "image": "real_life_q4",
        "text": "Назови главного врага, который ещё крадёт твой пресс:",
        "buttons": [
            ("🌙 Вечерний жор", [("score", -5), ("mistake", "вечерний жор"), ("progress", 20)], "to_boss"),
            ("🍬 Сладкое", [("score", -5), ("mistake", "сладкое"), ("progress", 20)], "to_boss"),
            ("⏭️ Пропуск еды", [("score", -5), ("mistake", "голод"), ("progress", 20)], "to_boss"),
        ],
    },
    "to_boss": {
        "image": None,
        "text": "Ты расправился с офисными драконами... Это Царство Пельменеса... Пора сразиться с боссом!",
        "buttons": [("🥟 В логово пельменя!", [], "boss_intro")],
    },
    "boss_intro": {
        "image": "boss_intro",
        "text": "🥟 ЦАРСТВО ПЕЛЬМЕНЕСА 🥟\n\n«Я — повелитель переедания! Твой пресс у меня в начинке! Ответишь на мой вопрос — получишь его обратно!»",
        "buttons": [("⚔️ Задать вопрос", [], "boss_riddle")],
    },
    "boss_riddle": {
        "image": "boss_riddle",
        "text": "Великий Пельменес ревёт: «Как правильно обращаться с вкусной, но вредной едой?»",
        "buttons": [
            ("🥟 Есть осознанно, иногда, не запрещая себе", [
                ("score", 20),
                ("inv", "Укротитель пельменей"),
                ("msg", "«Верно! Запреты порождают срывы.»"),
            ], "boss_victory"),
            ("🚫 Полностью запретить всё вкусное", [
                ("score", -10),
                ("mistake", "запреты"),
                ("msg", "«Это путь к срыву и качелям.»"),
            ], "boss_victory"),
            ("🍽 Есть всё подряд, жизнь одна", [
                ("score", -10),
                ("mistake", "вседозволенность"),
                ("msg", "«Жизнь одна — а пресс остаётся в начинке.»"),
            ], "boss_victory"),
        ],
    },
    "boss_victory": {
        "image": "boss_victory",
        "text": "🎉 Пельменес повержен! Из его недр вылетает последний фрагмент твоего пресса...",
        "buttons": [("🥄 Угостить сметанкой", [], "diagnostics")],
    },
    # diagnostics, offer, contact, end — handled with special logic below
}


# -------- Effect application --------

def apply_effects(uid, effects):
    s = get_state(uid)
    extra_msgs = []
    for eff in effects:
        kind = eff[0]
        if kind == "score":
            s["score"] += eff[1]
        elif kind == "progress":
            s["progress"] += eff[1]
        elif kind == "mistake":
            if eff[1] not in s["mistakes"]:
                s["mistakes"].append(eff[1])
        elif kind == "inv":
            if eff[1] not in s["inventory"]:
                s["inventory"].append(eff[1])
        elif kind == "guide":
            extra_msgs.append(("guide", eff[1]))
        elif kind == "msg":
            extra_msgs.append(("msg", eff[1]))
        elif kind == "set_gender":
            s["gender"] = eff[1]
        elif kind == "set_goal":
            s["goal"] = eff[1]
    return extra_msgs


def send_step(chat_id, step_id):
    uid = chat_id
    s = get_state(uid)
    s["step"] = step_id

    if step_id == "diagnostics":
        return send_diagnostics(chat_id)
    if step_id == "offer":
        return send_offer(chat_id)
    if step_id == "contact":
        return send_contact_request(chat_id)
    if step_id == "end":
        return send_end(chat_id)

    step = STEPS.get(step_id)
    if not step:
        send_text(chat_id, f"⚠️ Шаг {step_id} не найден. Нажми /start, чтобы начать сначала.")
        return

    img_key = step.get("image")
    if img_key and img_key in IMAGES:
        img_path = IMAGES[img_key]
        base = get_base_url()
        img_url = (base + img_path) if (base and img_path.startswith("/")) else img_path
        print(f"[img] sending {img_url}")
        send_photo(chat_id, img_url)

    if "inline" in step:
        send_text(chat_id, step["text"], inline_kb=step["inline"])
    elif step.get("input"):
        send_text(chat_id, step["text"], remove_kb=True)
    elif "buttons" in step:
        labels = [b[0] for b in step["buttons"]]
        send_text(chat_id, step["text"], reply_kb=labels)
    else:
        send_text(chat_id, step["text"])


def send_extras(chat_id, extras):
    for kind, val in extras:
        if kind == "msg":
            send_text(chat_id, val)
        elif kind == "guide":
            title = GUIDE_FILES.get(val, val)
            if BASE_URL:
                url = f"{BASE_URL}/guides/{val}"
                send_document(chat_id, url, caption=f"🎁 {title}")
            else:
                send_text(chat_id, f"🎁 Награда: {title}\n(файл будет доступен после деплоя)")


# -------- Diagnostics / offer / contact --------

def calc_kbju(s):
    g, age, h, w, goal = s["gender"], s["age"], s["height"], s["weight"], s["goal"]
    if not all([g, age, h, w, goal]):
        return None
    if g == "м":
        bmr = 10 * w + 6.25 * h - 5 * age + 5
    else:
        bmr = 10 * w + 6.25 * h - 5 * age - 161
    tdee = bmr * 1.5
    if goal == "сжечь жир":
        cal = tdee * 0.82
    elif goal == "набрать массу":
        cal = tdee * 1.1
    else:
        cal = tdee
    protein = round(w * (1.8 if goal != "энергия" else 1.4))
    fat = round(w * 1.0)
    carbs = round((cal - protein * 4 - fat * 9) / 4)
    return {"cal": round(cal), "protein": protein, "fat": fat, "carbs": carbs}


def send_diagnostics(chat_id):
    s = get_state(chat_id)
    send_photo(chat_id, get_base_url() + IMAGES["diagnostics"])
    kbju = calc_kbju(s)
    lines = [
        "📋 ДИАГНОСТИКА ОТ МАГИСТРА SERBOLIN'А",
        "",
        f"⭐ Очки дисциплины: {s['score']}",
        f"📦 Инвентарь: {len(s['inventory'])} артефакт(ов)",
    ]
    if s["inventory"]:
        for it in s["inventory"]:
            lines.append(f"   • {it}")
    if s["mistakes"]:
        lines.append("")
        lines.append("⚠️ Твои враги пресса (ошибки):")
        for m in s["mistakes"]:
            lines.append(f"   • {m}")
    else:
        lines.append("")
        lines.append("🛡️ У тебя нет уязвимостей — впечатляюще!")
    if kbju:
        lines += [
            "",
            "🍽️ Твои персональные нормы КБЖУ:",
            f"   Калории: {kbju['cal']} ккал",
            f"   Белки: {kbju['protein']} г",
            f"   Жиры: {kbju['fat']} г",
            f"   Углеводы: {kbju['carbs']} г",
        ]
    lines += [
        "",
        "Это лишь верхушка айсберга. Чтобы реально вернуть пресс и удержать его, нужен индивидуальный разбор твоей ситуации.",
    ]
    send_text(chat_id, "\n".join(lines))
    s["step"] = "offer"
    send_text(chat_id, "🎯 Магистр Serbolin приглашает тебя на БЕСПЛАТНУЮ консультацию.",
              reply_kb=["🎯 Оставить заявку (БЕСПЛАТНО)", "❌ Не сейчас"])


def send_offer(chat_id):
    send_photo(chat_id, get_base_url() + IMAGES["offer"])
    send_text(chat_id,
              "Оставь заявку на бесплатную консультацию — и магистр лично разберёт твою ситуацию.\n\nНажми кнопку ниже, чтобы поделиться контактом.",
              reply_kb=["📱 Отправить контакт", "❌ Не сейчас"])
    s = get_state(chat_id)
    s["step"] = "contact_wait"


def send_contact_request(chat_id):
    send_photo(chat_id, get_base_url() + IMAGES["contact"])
    # Use Telegram's request_contact button
    rm = {
        "keyboard": [[{"text": "📱 Поделиться номером", "request_contact": True}], [{"text": "❌ Не сейчас"}]],
        "resize_keyboard": True,
        "one_time_keyboard": True,
    }
    tg("sendMessage", chat_id=chat_id, text="Нажми кнопку ниже, чтобы отправить свой номер магистру.", reply_markup=rm)
    s = get_state(chat_id)
    s["step"] = "contact_wait"


def send_end(chat_id):
    send_photo(chat_id, get_base_url() + IMAGES["end"])
    send_text(chat_id,
              "🏆 Сага завершена. Магистр Serbolin свяжется с тобой в ближайшее время.\n\nЧтобы пройти заново — нажми /start.",
              remove_kb=True)


def forward_lead(s, user, contact=None):
    lines = [
        "🆕 НОВАЯ ЗАЯВКА из Саги о потерянном прессе",
        "",
        f"Имя: {user.get('first_name','')} {user.get('last_name','') or ''}".strip(),
        f"Username: @{user.get('username','—')}",
        f"User ID: {user.get('id')}",
    ]
    if contact:
        lines.append(f"Телефон: {contact.get('phone_number')}")
    lines += [
        "",
        f"Пол: {s.get('gender')}",
        f"Возраст: {s.get('age')}",
        f"Рост/вес: {s.get('height')}/{s.get('weight')}",
        f"Цель: {s.get('goal')}",
        f"Очки: {s.get('score')}",
        f"Ошибки: {', '.join(s.get('mistakes', [])) or '—'}",
    ]
    tg("sendMessage", chat_id=OWNER_ID, text="\n".join(lines))


# -------- Update processing --------

def handle_button(chat_id, user, text):
    s = get_state(chat_id)

    # Contact / offer states
    if s["step"] == "contact_wait":
        if text == "❌ Не сейчас":
            send_end(chat_id)
            return
        if text == "📱 Отправить контакт":
            send_contact_request(chat_id)
            return

    # Offer step buttons
    if s["step"] == "offer":
        if text == "🎯 Оставить заявку (БЕСПЛАТНО)":
            send_contact_request(chat_id)
            return
        if text == "❌ Не сейчас":
            send_end(chat_id)
            return

    # Input steps
    if s["step"] == "ask_age":
        if text.isdigit() and 14 <= int(text) <= 100:
            s["age"] = int(text)
            send_step(chat_id, "ask_body")
        else:
            send_text(chat_id, "🚫 Введи реальный возраст (14–100)")
        return
    if s["step"] == "ask_body":
        parts = text.split()
        if len(parts) == 2 and all(p.isdigit() for p in parts):
            s["height"] = int(parts[0])
            s["weight"] = int(parts[1])
            send_step(chat_id, "ask_goal")
        else:
            send_text(chat_id, "🚫 Введи два числа через пробел, например: 180 80")
        return

    # Regular step buttons
    step = STEPS.get(s["step"])
    if not step or "buttons" not in step:
        send_text(chat_id, "Используй кнопки, странник. Или нажми /start.")
        return
    for label, effects, next_step in step["buttons"]:
        if label == text:
            extras = apply_effects(chat_id, effects)
            send_extras(chat_id, extras)
            send_step(chat_id, next_step)
            return
    send_text(chat_id, "Выбери один из вариантов кнопкой ниже.")


def handle_callback(chat_id, user, data):
    if data == "check_sub":
        if is_subscribed(chat_id):
            send_text(chat_id, "✅ Ты в гильдии! Врата открываются...")
            send_step(chat_id, "firstChoice")
        else:
            send_text(chat_id, "❌ Не вижу подписки. Подпишись на канал и нажми «Я подписался» ещё раз.")
        return


def process_update(update):
    try:
        if "callback_query" in update:
            cq = update["callback_query"]
            chat_id = cq["from"]["id"]
            tg("answerCallbackQuery", callback_query_id=cq["id"])
            handle_callback(chat_id, cq["from"], cq.get("data", ""))
            save_states()
            return

        msg = update.get("message") or update.get("edited_message")
        if not msg:
            return
        chat_id = msg["chat"]["id"]
        user = msg.get("from", {})

        if "contact" in msg:
            s = get_state(chat_id)
            forward_lead(s, user, msg["contact"])
            send_text(chat_id, "✅ Заявка отправлена магистру. Он свяжется с тобой в ближайшее время.")
            send_end(chat_id)
            save_states()
            return

        text = (msg.get("text") or "").strip()
        if text == "/start":
            reset_state(chat_id)
            send_step(chat_id, "intro_welcome")
            save_states()
            return
        if text == "/reset":
            reset_state(chat_id)
            send_text(chat_id, "Состояние сброшено. Нажми /start.")
            save_states()
            return

        handle_button(chat_id, user, text)
        save_states()
    except Exception as e:
        print("process_update error:", e)
        traceback.print_exc()


# -------- HTTP handler (Vercel entry) --------

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        global _runtime_base_url
        host = self.headers.get("host", "")
        if host and not _runtime_base_url:
            _runtime_base_url = f"https://{host}"
            print(f"[boot] runtime base URL set to {_runtime_base_url}")

        length = int(self.headers.get("content-length", 0))
        body = self.rfile.read(length) if length else b"{}"
        try:
            update = json.loads(body.decode("utf-8") or "{}")
            process_update(update)
        except Exception as e:
            print("handler error:", e)
            traceback.print_exc()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK")

    def do_GET(self):
        path = self.path.split("?", 1)[0].rstrip("/") or "/"
        if path.endswith("/setup"):
            host = self.headers.get("host", "")
            base = f"https://{host}" if host else BASE_URL
            webhook_url = f"{base}/webhook"
            result = tg("setWebhook", url=webhook_url, drop_pending_updates=True)
            info_resp = tg("getWebhookInfo")
            body = json.dumps(
                {"setWebhook": result, "getWebhookInfo": info_resp, "webhook_url": webhook_url},
                ensure_ascii=False,
                indent=2,
            ).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(body)
            return

        if path.endswith("/debug"):
            host = self.headers.get("host", "")
            base = f"https://{host}" if host else (BASE_URL or "(unknown)")
            test_img_url = base + "/img/intro.jpeg"
            try:
                req = urllib.request.Request(test_img_url, method="HEAD")
                with urllib.request.urlopen(req, timeout=5) as r:
                    img_status = f"OK {r.status}"
            except Exception as ex:
                img_status = f"FAIL: {ex}"
            webhook_info = tg("getWebhookInfo") or {}
            debug = {
                "base_url_env": BASE_URL,
                "base_url_runtime": _runtime_base_url,
                "base_url_used": base,
                "test_image_url": test_img_url,
                "test_image_fetch": img_status,
                "vercel_url_env": VERCEL_URL,
                "webhook": webhook_info.get("result", {}),
            }
            body = json.dumps(debug, ensure_ascii=False, indent=2).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(body)
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        host = self.headers.get("host", "")
        base = f"https://{host}" if host else (BASE_URL or "(unknown)")
        info = (
            f"Saga bot is alive. Base URL: {base}\n"
            f"Open {base}/setup to register the Telegram webhook.\n"
            f"Open {base}/debug to diagnose image delivery."
        )
        self.wfile.write(info.encode("utf-8"))
