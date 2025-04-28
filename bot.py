import logging
from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    Filters
)
from handlers import (
    start_command,
    help_command,
    signals_command,
    button_callback,
    generate_keys_command,
    list_keys_command,
    process_potential_key,
    admin_panel,
    error_handler
)
from config import BOT_TOKEN

logger = logging.getLogger(__name__)

def setup_bot():
    """
    Set up and configure the Telegram bot.
    
    Returns:
        Updater: The configured bot updater
    """
    if not BOT_TOKEN:
        logger.error("No bot token provided! Bot cannot start.")
        return None
    
    # Create the Updater and pass it your bot's token
    updater = Updater(BOT_TOKEN)
    
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    
    # Register command handlers
    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("signals", signals_command))
    
    # Add message handler for authentication keys
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, process_potential_key))
    
    # Admin commands
    dispatcher.add_handler(CommandHandler("admin", admin_panel))
    dispatcher.add_handler(CommandHandler("generate_keys", generate_keys_command))
    dispatcher.add_handler(CommandHandler("list_keys", list_keys_command))
    
    # Register callback query handler for buttons
    dispatcher.add_handler(CallbackQueryHandler(button_callback))
    
    # Register error handler
    dispatcher.add_error_handler(error_handler)
    
    logger.info("Bot setup completed!")
    return updater

def run_bot():
    """Start the bot"""
    updater = setup_bot()
    if updater:
        logger.info("Starting bot...")
        updater.start_polling()
        updater.idle()
    else:
        logger.error("Bot setup failed!")