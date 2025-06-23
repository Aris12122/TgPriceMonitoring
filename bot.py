from collections import defaultdict
import asyncio
import aiohttp
from telebot.async_telebot import AsyncTeleBot
import os


from dotenv import load_dotenv
load_dotenv("secrets.env")

TG_BOT_KEY = os.getenv('TG_BOT_KEY')
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET')
CHECK_INTERVAL = 60
ALERT_THRESHOLD = 1.0


bot = AsyncTeleBot(TG_BOT_KEY)


class CryptoMonitor:
    """Класс для мониторинга криптовалют для конкретного пользователя и крипты"""
    _all_monitors = defaultdict(dict)  # {user_id: {symbol: monitor_instance}}
    
    def __init__(self, user_id, symbol):
        """Инициализация мониторинга"""
        self.user_id = user_id
        self.symbol = symbol
        self.last_price = None
        self.alert_threshold = ALERT_THRESHOLD
        self.is_active = True
    

    @classmethod
    async def create(cls, user_id, symbol):
        """Асинхронный конструктор"""
        self = cls(user_id, symbol)
        self.last_price = await self.get_current_price()
        cls._all_monitors[user_id][symbol] = self
        return self
    

    async def get_current_price(self):
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://api.binance.com/api/v3/ticker/price?symbol={self.symbol}"
                async with session.get(url) as response:
                    data = await response.json()
                    return float(data['price'])
        except Exception as e:
            print(f"Ошибка получения цены для {self.symbol}: {e}")
            return None
    

    async def check_price(self):
        """Проверка изменения цены и отправка алерта"""
        if not self.is_active:
            return
            
        current_price = await self.get_current_price()
        if current_price is None or self.last_price is None:
            self.last_price = current_price
            return
        
        change_percent = (current_price - self.last_price) * 100. / self.last_price
        
        if abs(change_percent) >= self.alert_threshold:
            direction = "Рост" if change_percent > 0 else "Падение"
            message = (
                f"ALERT *Изменение цены {self.symbol}*\n"
                f"{direction} на *{abs(change_percent):.2f}%*\n"
                f"Текущая цена: ${current_price:.4f}"
            )
            
            try:
                await bot.send_message(self.user_id, message, parse_mode="Markdown")
            except Exception as e:
                print(f"Ошибка отправки сообщения: {e}")
        
        self.last_price = current_price
    

    @classmethod
    async def check_all_monitors(cls):
        tasks = []
        for user_monitors in cls._all_monitors.values():
            for monitor in user_monitors.values():
                if monitor.is_active:
                    tasks.append(monitor.check_price())
        
        await asyncio.gather(*tasks, return_exceptions=True)
    

    @classmethod
    def get_user_monitors(cls, user_id):
        return cls._all_monitors.get(user_id, {})
    

    @classmethod
    def remove_monitor(cls, user_id, symbol):
        if user_id in cls._all_monitors and symbol in cls._all_monitors[user_id]:
            cls._all_monitors[user_id][symbol].is_active = False
            del cls._all_monitors[user_id][symbol]
            return True
        return False


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