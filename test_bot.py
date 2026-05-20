import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

BOT_TOKEN = "8950032855:AAF3puz71ztCKrXMJEdgq8je9K8Cjr7EhOg"

async def main():
    bot = Bot(token=BOT_TOKEN)
    logging.info("Бот создан успешно!")
    await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
