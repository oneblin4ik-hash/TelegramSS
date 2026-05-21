# Сага о потерянном прессе — Telegram-бот на Vercel

Telegram-бот квест-игры в фэнтези-мире Фитосферы. Деплоится как Python serverless function на Vercel.

## Структура

```
.
├── api/bot.py           # Webhook handler (stdlib only)
├── public/guides/       # PDF-награды (раздаются статически)
├── vercel.json          # Конфиг Vercel
├── requirements.txt     # Пусто (только stdlib)
└── guides/              # Исходники PDF (можно удалить после деплоя)
```

## Деплой за 5 минут

### 1. Импорт в Vercel
1. Открой https://vercel.com/new
2. Импортируй репозиторий `oneblin4ik-hash/TelegramSS`
3. **Branch**: `claude/deploy-game-vercel-o1Dle` (или `main` после мерджа PR)
4. **Framework Preset**: Other
5. **Root Directory**: оставь как есть
6. Не нажимай Deploy сразу — сначала добавь переменные окружения 👇

### 2. Environment Variables
Добавь в настройках проекта на Vercel:

| Имя         | Значение                                                |
|-------------|---------------------------------------------------------|
| `BOT_TOKEN` | `8950032855:AAF3puz71ztCKrXMJEdgq8je9K8Cjr7EhOg`        |
| `OWNER_ID`  | `708122486`                                             |
| `CHANNEL_ID`| `-1002095605776`                                        |

`VERCEL_URL` подставляется автоматически — добавлять не нужно.

### 3. Deploy
Нажми **Deploy**. Дождись «Ready». Скопируй URL проекта (например, `saga-bot-xyz.vercel.app`).

### 4. Установить webhook
В терминале (один раз):

```bash
curl "https://api.telegram.org/bot8950032855:AAF3puz71ztCKrXMJEdgq8je9K8Cjr7EhOg/setWebhook?url=https://<твой-проект>.vercel.app/webhook"
```

Должен прийти ответ `{"ok":true, ...}`.

### 5. Готово
Открой бота в Telegram (`@<имя_бота>`), нажми `/start`. Игра должна запуститься.

## Проверка

- `GET https://<твой-проект>.vercel.app/` → `Saga bot is alive…`
- `GET https://<твой-проект>.vercel.app/guides/13_sovetov.pdf` → должен скачать PDF
- Webhook: `curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo`

## Особенности

- **Состояние игроков** хранится в памяти процесса + `/tmp/saga_states.json`. На холодном старте может сбрасываться — для MVP-демо приемлемо. При нагрузке стоит вынести в Vercel KV / Upstash Redis.
- **Картинки** грузятся напрямую с Imgur — Telegram кеширует их у себя после первого использования.
- **Гайды (PDF)** раздаются статически через `/guides/*.pdf`.
- **Проверка подписки**: бот должен быть админом канала с `CHANNEL_ID = -1002095605776`.

## Команды бота

- `/start` — начать игру с нуля
- `/reset` — сброс состояния

## Известные TODO

- Перенести `BOT_TOKEN` полностью на env vars (сейчас есть fallback в коде — отозвать токен у BotFather и обновить env var на Vercel).
- Внешнее хранилище состояния для холодных стартов.
