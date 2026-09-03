import logging
import os
import sys
import json
import urllib.request
from threading import Thread
from flask import Flask
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

# I-load dagiti environment variable manipud iti .env file
load_dotenv()

# I-setup ti logging system
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def fetch_token_from_api() -> str:
    """I-fetch ti Bot Token manipud iti API URL no awan iti environment variable."""
    api_url = "https://api.ayanapi.workers.dev/"
    try:
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                # I-check dagiti nalabit a key name manipud API response
                token = data.get("bot_token") or data.get("token") or data.get("BOT_TOKEN")
                if token:
                    logger.info("Nasarakansan ti Bot Token manipud iti API.")
                    return token
    except Exception as e:
        logger.warning(f"Saan a naala ti token manipud API: {e}")
    return ""

# I-validate ti Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    BOT_TOKEN = fetch_token_from_api()

if not BOT_TOKEN:
    logger.critical("Mabalin a pammusat: Awan ti BOT_TOKEN iti .env wenno API.")
    sys.exit(1)

# I-initialize ti Flask App para iti Render Web Service Health Check
flask_app = Flask(__name__)

@flask_app.route("/", methods=["GET"])
def health_check():
    """Endpoint para iti health check ti Render server."""
    return "Bot is running successfully!", 200

def run_flask():
    """Patarayen ti Flask server iti target port."""
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)

# --- HANDLERS PARA KADAGITI TELEGRAM COMMAND ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para iti /start command."""
    user = update.effective_user
    chat_id = update.effective_chat.id

    logger.info(
        f"GUMAM-AMBONG /start - User ID: {user.id}, Username: @{user.username}, "
        f"Naranas: {user.first_name}, Chat ID: {chat_id}"
    )

    # Mensahe ti kablaaw iti Bangla
    message = (
        "👋 <b>স্বাগতম!</b>\n\n"
        "আমাদের ওয়েবসাইটটি একবার ঘুরে দেখুন। সেখানে আরও সুন্দর কনটент ও ফিচার রয়েছে।"
    )

    # Inline Keyboard Button para iti website
    keyboard = [
        [
            InlineKeyboardButton(text="🌐 Visit Website", url="https://arian00001.site")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        text=message,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )

async def chatid_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para iti /chatid command."""
    user = update.effective_user
    chat_id = update.effective_chat.id
    username_str = f"@{user.username}" if user.username else "Awan ti username"

    # Nataer ken nadalus a HTML format para iti chat information
    message = (
        "<b>🆔 Your Telegram Information</b>\n\n"
        f"<b>Chat ID:</b> <code>{chat_id}</code>\n"
        f"<b>User ID:</b> <code>{user.id}</code>\n"
        f"<b>Username:</b> {username_str}"
    )

    await update.message.reply_text(
        text=message,
        parse_mode=ParseMode.HTML
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para iti /help command."""
    message = (
        "<b>Available Commands:</b>\n\n"
        "/start - Start the bot\n"
        "/chatid - Get your Chat ID and User ID\n"
        "/help - Show help"
    )

    await update.message.reply_text(
        text=message,
        parse_mode=ParseMode.HTML
    )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """I-log dagiti babbaso wenno exception nga mapasamak."""
    logger.error(msg="Rumesngad a babbaso:", exc_info=context.error)

def main() -> None:
    """I-start ti Flask server ken ti Telegram bot application."""
    # 1. Patarayen ti Flask background thread para iti Render health check
    logger.info("Nangrugi ti Flask health endpoint thread...")
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # 2. I-build ti Telegram Bot Application
    logger.info("I-initialize ti Telegram Bot...")
    bot_app = Application.builder().token(BOT_TOKEN).build()

    # I-rekord dagiti Command Handler
    bot_app.add_handler(CommandHandler("start", start_command))
    bot_app.add_handler(CommandHandler("chatid", chatid_command))
    bot_app.add_handler(CommandHandler("help", help_command))

    # I-rekord ti Error Handler
    bot_app.add_error_handler(error_handler)

    # 3. Patarayen ti Polling
    logger.info("Nangrugi ti bot iti polling mode...")
    bot_app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
