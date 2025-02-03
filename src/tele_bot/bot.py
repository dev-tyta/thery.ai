#TODO: Collate the necessary features for the Telegram bot, including parts like buttons, other services, Web Search Feature (*Might be nice to try this out.*)

import asyncio
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackContext
)

from src.llm.agents.conversation_agent import ConversationAgent
from src.llm.models.schemas import SessionData
from src.llm.core.config import settings

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

conversation_agent = ConversationAgent()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command with interactive keyboard"""
    keyboard = [
        ["💬 Start Chatting"],
        ["ℹ️ About", "🛠 Help"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    welcome_msg = (
        "🌟 Welcome to Thery AI! 🌟\n\n"
        "I'm here to provide compassionate mental health support. "
        "How can I help you today?"
    )
    
    await update.message.reply_text(welcome_msg, reply_markup=reply_markup)

async def handle_message(update: Update, context: CallbackContext):
    """Process user messages with conversation context"""
    try:
        user = update.effective_user
        text = update.message.text
        
        # Get or create session
        session_data = context.user_data.get('session_data')
        
        # Process query
        response = await conversation_agent.process_async(
            query=text,
            session_data=session_data
        )
        
        # Update session data
        context.user_data['session_data'] = response.session_data
        
        # Send response with typing indicator
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="typing"
        )
        await update.message.reply_text(response.response)

    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        await update.message.reply_text("I'm having trouble understanding. Let's try that again.")


async def error_handler(update: Update, context: CallbackContext):
    """Handle errors in the bot"""
    logger.error(f"Update {update} caused error: {context.error}")
    await update.message.reply_text("Oops! Something went wrong. Please try again.")


def main():
    """Configure and start the bot"""
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Add error handler
    application.add_error_handler(error_handler)

    # Start polling
    logger.info("Starting Thery AI Telegram bot...")
    application.run_polling(
        poll_interval=1,
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )

if __name__ == "__main__":
    main()