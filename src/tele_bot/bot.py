import asyncio
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackContext,
)

from src.llm.agents.conversation_agent import ConversationAgent
from src.llm.models.schemas import SessionData
from src.llm.core.config import settings

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

conversation_agent = ConversationAgent()

MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [["💬 Start Chatting"], ["ℹ️ About", "🛠 Help"]],
    resize_keyboard=True,
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    context.user_data.clear()
    welcome_msg = (
        "🌟 Welcome to Thery AI! 🌟\n\n"
        "I'm here to provide compassionate mental health support. "
        "How can I help you today?"
    )
    await update.message.reply_text(welcome_msg, reply_markup=MAIN_KEYBOARD)


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /about command."""
    text = (
        "ℹ️ *About Thery AI*\n\n"
        "Thery AI is a compassionate virtual therapist backed by Google Gemini. "
        "It offers empathetic, evidence-based support for mental wellness. "
        "It is *not* a replacement for professional medical care."
    )
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=MAIN_KEYBOARD)


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    text = (
        "🛠 *Help*\n\n"
        "• Just type your thoughts — Thery AI will respond.\n"
        "• Use /start to reset your session.\n"
        "• Use /about to learn more about the bot.\n\n"
        "In a crisis? Please reach out to a local emergency service or crisis hotline."
    )
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=MAIN_KEYBOARD)


async def handle_message(update: Update, context: CallbackContext) -> None:
    """Process user messages with conversation context."""
    text = update.message.text

    # Intercept keyboard button presses
    if text == "ℹ️ About":
        await about(update, context)
        return
    if text == "🛠 Help":
        await help_cmd(update, context)
        return
    if text == "💬 Start Chatting":
        await update.message.reply_text(
            "Great! Tell me what's on your mind. 😊", reply_markup=MAIN_KEYBOARD
        )
        return

    # Show typing indicator while processing
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action="typing"
    )

    try:
        session_data = context.user_data.get("session_data")

        response = await conversation_agent.process_async(
            query=text,
            session_data=session_data,
        )

        context.user_data["session_data"] = response.session_data

        await update.message.reply_text(response.response, reply_markup=MAIN_KEYBOARD)

    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await update.message.reply_text(
            "I'm having a little trouble right now. Please try again in a moment. 🙏",
            reply_markup=MAIN_KEYBOARD,
        )


async def error_handler(update: object, context: CallbackContext) -> None:
    """Log and notify on unhandled errors."""
    logger.error(f"Update {update} caused error: {context.error}")
    if isinstance(update, Update) and update.message:
        await update.message.reply_text(
            "Oops! Something went wrong. Please try again.", reply_markup=MAIN_KEYBOARD
        )


def main() -> None:
    """Configure and start the bot."""
    if not settings.TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set in .env")

    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("about", about))
    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )
    application.add_error_handler(error_handler)

    logger.info("Starting Thery AI Telegram bot...")
    application.run_polling(
        poll_interval=1,
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()