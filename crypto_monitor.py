import asyncio
from collections import defaultdict
import aiohttp

ALERT_THRESHOLD = 1.0


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