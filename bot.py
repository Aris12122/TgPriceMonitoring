import asyncio
import aiohttp
from telebot.async_telebot import AsyncTeleBot
import os
from crypto_monitor import CryptoMonitor


from dotenv import load_dotenv
load_dotenv("secrets.env")

TG_BOT_KEY = os.getenv('TG_BOT_KEY')
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET')
CHECK_INTERVAL = 60


bot = AsyncTeleBot(TG_BOT_KEY)


@bot.message_handler(commands=['start', 'help'])
async def send_welcome(message):
    await bot.reply_to(
        message,
        "Привет! Я бот для мониторинга цен криптовалют на Binance\n"
        "Используй команды:\n"
        "/add_symbol BTCUSDT — добавить мониторинг\n"
        "/list_monitors — список активных мониторингов\n"
        "/remove_monitor BTCUSDT — удалить мониторинг"
    )



@bot.message_handler(commands=['add_symbol'])
async def add_monitor_command(message):
    user_id = message.chat.id
    if not message.text or len(message.text.split()) < 2:
        await bot.reply_to(message, "Укажите символ криптовалюты (например: /add_symbol BTCUSDT)")
        return
    
    symbol = message.text.split()[1].upper()
    
    if symbol in CryptoMonitor.get_user_monitors(user_id):
        await bot.reply_to(message, f"Мониторинг для {symbol} уже активен!")
        return
    
    try:
        monitor = await CryptoMonitor.create(user_id, symbol)
        await bot.reply_to(
            message,
            f"Мониторинг для {symbol} запущен!\nТекущая цена: ${monitor.last_price:.4f}"
        )
    except Exception as e:
        print(f"Ошибка создания мониторинга: {e}")
        await bot.reply_to(message, f"Ошибка: {e}\nПроверьте правильность символа")



@bot.message_handler(commands=['list_monitors'])
async def list_monitors_command(message):
    user_id = message.chat.id
    monitors = CryptoMonitor.get_user_monitors(user_id)
    
    if not monitors:
        await bot.reply_to(message, "У вас нет активных мониторингов.")
        return
    
    response = "Ваши активные мониторинги:\n\n"
    for symbol, monitor in monitors.items():
        response += f"• {symbol}: ${monitor.last_price:.4f}\n"
    
    await bot.reply_to(message, response)



@bot.message_handler(commands=['remove_monitor'])
async def remove_monitor_command(message):
    user_id = message.chat.id
    if not message.text or len(message.text.split()) < 2:
        await bot.reply_to(message, "Укажите символ криптовалюты (например: /remove_monitor BTCUSDT)")
        return
    
    symbol = message.text.split()[1].upper()
    
    if CryptoMonitor.remove_monitor(user_id, symbol):
        await bot.reply_to(message, f"Мониторинг для {symbol} остановлен")
    else:
        await bot.reply_to(message, f"Активный мониторинг для {symbol} не найден")



async def background_monitor_task():
    while True:
        try:
            await CryptoMonitor.check_all_monitors()
        except Exception as e:
            print(f"Ошибка при проверке цен check_all_monitors: {e}")
        await asyncio.sleep(CHECK_INTERVAL)



async def main():
    asyncio.create_task(background_monitor_task())
    
    await bot.infinity_polling()


if __name__ == "__main__":
    asyncio.run(main())