# Telegram Bot

This project is a simple Telegram bot that responds with "hello" to any incoming message. It is built using the Telebot package.

## Project Structure

```
telegram-bot
├── src
│   ├── bot.py        # Main logic for the Telegram bot
│   └── config.py     # Contains the API key for the Telegram bot
├── .gitignore        # Specifies files to be ignored by Git
├── requirements.txt  # Lists project dependencies
└── README.md         # Project documentation
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd telegram-bot
   ```

2. **Create a virtual environment (optional but recommended):**
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

4. **Set up your API key:**
   - Create a file named `config.py` in the `src` directory and add your Telegram bot API key:
     ```python
     API_KEY = 'your_api_key_here'
     ```

5. **Run the bot:**
   ```
   python src/bot.py
   ```

## Usage

Once the bot is running, it will listen for incoming messages and respond with "hello" to any message received.

## Note

Make sure to add `src/config.py` to your `.gitignore` file to keep your API key secure and prevent it from being tracked by Git.