# TgPriceMonitoring

Асинхронный мониторинг цен криптовалют на Binance

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd TgPriceMonitoring
   ```

2. **Create a virtual environment (optional but recommended):**
   ```
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

4. **Set up your API key:**
   - Create a file named `secrets.env` in the directory and add your Telegram bot API key:
     ```python
     TG_BOT_KEY = 'your_api_key_here'
     ```

5. **Run the bot:**
   ```
   python bot.py
   ```

## Usage

Когда бот запущен, можете протестировать его в телеграм.
