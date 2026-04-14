import asyncio
from aiogram import Bot, Dispatcher
from handlers import router

async def main():
    bot = Bot(token="8713575377:AAFad5R1Q4PShKRuym_-aOxJf142TLLOgaU")
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())