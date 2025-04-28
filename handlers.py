import logging
from datetime import datetime, timedelta
from functools import wraps
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext
from config import (
    AUTHENTICATED_USERS,
    VALID_KEYS,
    USED_KEYS,
    WELCOME_MESSAGE,
    HELP_MESSAGE,
    AUTHENTICATION_SUCCESS,
    AUTHENTICATION_FAILURE,
    SIGNALS_FETCH_ERROR,
    NO_SIGNALS_AVAILABLE
)
from utils import (
    verify_private_key, 
    fetch_trading_signals, 
    format_signal_message,
    generate_new_key,
    get_all_valid_keys
)

logger = logging.getLogger(__name__)

# Decorator to check authentication
def check_authentication(func):
    @wraps(func)
    def wrapped(update: Update, context: CallbackContext, *args, **kwargs):
        if update.effective_user is None:
            return

        user_id = update.effective_user.id

        if user_id in AUTHENTICATED_USERS:
            return func(update, context, *args, **kwargs)
        else:
            keyboard = [
                [InlineKeyboardButton("Authenticate", callback_data="authenticate")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            # Store the original command in user_data for later execution
            if update.message and update.message.text:
                context.user_data['pending_command'] = update.message.text

            update.message.reply_text(
                "*Authentication Required*\n\n"
                "Please enter your private key to continue.\n"
                "Contact admin @BILLIONAIREBOSS101 if you don't have one.",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            return
    return wrapped

def start_command(update: Update, context: CallbackContext):
    """Handle the /start command"""
    if update.effective_user is None:
        return

    keyboard = [
        [InlineKeyboardButton("Authenticate", callback_data="authenticate")],
        [InlineKeyboardButton("Get Signals", callback_data="get_signals")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        WELCOME_MESSAGE,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

def help_command(update: Update, context: CallbackContext):
    """Handle the /help command"""
    update.message.reply_text(
        HELP_MESSAGE,
        parse_mode='Markdown'
    )

def process_potential_key(update: Update, context: CallbackContext):
    """Process any message as a potential authentication key"""
    if update.effective_user is None or update.message is None:
        return

    user_id = update.effective_user.id
    message_text = update.message.text

    # Skip processing of command messages
    if message_text.startswith('/'):
        return

    # Skip if user is already authenticated
    if user_id in AUTHENTICATED_USERS:
        return

    # Process the message as a potential key
    private_key = message_text.strip()

    # Try to delete the message to protect the key
    try:
        context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.message.message_id
        )
    except Exception as e:
        logger.warning(f"Could not delete key message: {e}")

    # Verify the private key
    if verify_private_key(private_key):
        # Add user to authenticated users
        AUTHENTICATED_USERS.add(user_id)
        keyboard = [[InlineKeyboardButton("Get Signals", callback_data="get_signals")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(
            AUTHENTICATION_SUCCESS,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    else:
        update.message.reply_text(
            AUTHENTICATION_FAILURE,
            parse_mode='Markdown'
        )

@check_authentication
def signals_command(update: Update, context: CallbackContext):
    """Handle the /signals command"""
    update.message.reply_text("⏳ Fetching latest signals... Please wait.")

    signals = fetch_trading_signals()

    if not signals:
        update.message.reply_text(
            NO_SIGNALS_AVAILABLE,
            parse_mode='Markdown'
        )
        return

    # Get only the next immediate signal
    next_signal = signals[0] if signals else None

    if next_signal:
        message = format_signal_message(next_signal)
        try:
            # Send image with caption
            with open('static/images/billionaire_ai_bot.png', 'rb') as photo:
                context.user_data['current_signal'] = next_signal
                msg = update.message.reply_photo(
                    photo=photo,
                    caption=message,
                    parse_mode='Markdown'
                )

                # Schedule expiry check after 2 minutes from signal time  
                try:
                    # Remove timezone info for consistent comparison
                    signal_time_str = next_signal['converted_time'].split(' ')[0:2]
                    signal_time = datetime.strptime(' '.join(signal_time_str), "%Y-%m-%d %H:%M:%S")
                    current_time = datetime.now()

                    delay = (signal_time + timedelta(minutes=2) - current_time).total_seconds()

                    if delay > 0:
                        logger.info(f"Scheduling expiry check in {delay} seconds")
                        context.job_queue.run_once(
                            check_signal_expiry,
                            delay,
                            context={'chat_id': update.effective_chat.id, 'signal': next_signal},
                            name=f"expiry_{signal_time.strftime('%Y%m%d_%H%M%S')}"
                        )
                except Exception as e:
                    logger.error(f"Error scheduling expiry check: {e}")

        except FileNotFoundError:
            # Fallback to text-only if image not found
            update.message.reply_text(
                message,
                parse_mode='Markdown'
            )

def check_signal_expiry(context: CallbackContext):
    """Check if a signal has expired and send expiry message"""
    job = context.job
    chat_id = job.context['chat_id']
    signal = job.context['signal']

    # Send expiry message
    expiry_message = format_signal_message(signal, is_expiry=True)
    context.bot.send_message(
        chat_id=chat_id,
        text=expiry_message,
        parse_mode='Markdown'
    )

def button_callback(update: Update, context: CallbackContext):
    """Handle button callbacks"""
    query = update.callback_query
    query.answer()

    if query.data == "get_signals":
        # For button callbacks, we need to handle signals directly
        # Check if user is authenticated
        user_id = query.from_user.id
        if user_id not in AUTHENTICATED_USERS:
            query.message.reply_text(
                AUTHENTICATION_FAILURE,
                parse_mode='Markdown'
            )
            return

        # Get and send signals
        query.message.reply_text("⏳ Fetching latest signal... Please wait.")
        signals = fetch_trading_signals()

        if not signals:
            query.message.reply_text(
                NO_SIGNALS_AVAILABLE,
                parse_mode='Markdown'
            )
            return

        # Get only the next immediate signal
        next_signal = signals[0] if signals else None

        if next_signal:
            message = format_signal_message(next_signal)
            try:
                # Send image with caption
                with open('static/images/billionaire_ai_bot.png', 'rb') as photo:
                    query.message.reply_photo(
                        photo=photo,
                        caption=message,
                        parse_mode='Markdown'
                    )
                    # Schedule expiry check after 2 minutes from signal time
                    try:
                        signal_time_str = next_signal['converted_time'].split(' ')[0:2]
                        signal_time = datetime.strptime(' '.join(signal_time_str), "%Y-%m-%d %H:%M:%S")
                        current_time = datetime.now()
                        delay = (signal_time + timedelta(minutes=2) - current_time).total_seconds()

                        if delay > 0:
                            logger.info(f"Scheduling expiry check for signal after {delay} seconds")
                            context.job_queue.run_once(
                                check_signal_expiry,
                                delay,
                                context={'chat_id': query.message.chat_id, 'signal': next_signal},
                                name=f"expiry_{signal_time.strftime('%Y%m%d_%H%M%S')}"
                            )
                    except Exception as e:
                        logger.error(f"Error scheduling expiry check: {e}")
            except FileNotFoundError:
                # Fallback to text-only if image not found
                query.message.reply_text(
                    message,
                    parse_mode='Markdown'
                )

    elif query.data == "generate_signals":
        # Check if user is authenticated
        user_id = query.from_user.id
        if user_id not in AUTHENTICATED_USERS:
            query.message.reply_text(
                AUTHENTICATION_FAILURE,
                parse_mode='Markdown'
            )
            return

        # Execute /signals command functionality
        signals_command(query.callback_query, context)

    elif query.data == "authenticate":
        # Ask for the key directly without mentioning /auth command
        query.message.reply_text(
            "*Authentication Required*\n\n"
            "To get access to trading signals, please:\n"
            "1. Contact admin @BILLIONAIREBOSS101 to get your private key\n"
            "2. *Enter your private key in the chat*\n\n"
            "Only users with valid private keys can access the signals.",
            parse_mode='Markdown'
        )

def generate_keys_command(update: Update, context: CallbackContext):
    """
    Handle the /generate_keys command
    Admin-only command to generate new single-use keys
    """
    if update.effective_user is None:
        return

    user_id = update.effective_user.id
    user_name = update.effective_user.username

    # Check if the user is an admin
    ADMIN_USERNAMES = ["BILLIONAIREBOSS101", "Gazew_07"]

    if user_name not in ADMIN_USERNAMES:
        update.message.reply_text(
            "⛔ *Admin Access Required*\n\n"
            "Only admin users can generate new keys.",
            parse_mode='Markdown'
        )
        return

    # Get the count of keys to generate from the command args
    count = 5  # Default count
    if context.args and len(context.args) > 0:
        try:
            count = int(context.args[0])
            # Limit the number of keys to prevent spam
            if count > 20:
                count = 20
        except ValueError:
            pass

    # Generate new single-use keys
    new_keys = []
    for _ in range(count):
        key = generate_new_key()
        if key:
            new_keys.append(key)

    if not new_keys:
        update.message.reply_text(
            "❌ *Error Generating Keys*\n\n"
            "Failed to generate new keys. Please try again later.",
            parse_mode='Markdown'
        )
        return

    # Format the response message
    keys_list = "\n".join([f"• `{key}`" for key in new_keys])

    update.message.reply_text(
        f"🔑 *New Single-Use Keys Generated*\n\n"
        f"Generated {len(new_keys)} new single-use keys:\n\n"
        f"{keys_list}\n\n"
        f"_These keys can only be used once. After use, they will expire._",
        parse_mode='Markdown'
    )

def list_keys_command(update: Update, context: CallbackContext):
    """
    Handle the /list_keys command
    Admin-only command to list all unused keys
    """
    if update.effective_user is None:
        return

    user_name = update.effective_user.username

    # Check if the user is an admin
    ADMIN_USERNAMES = ["BILLIONAIREBOSS101", "Gazew_07"]

    if user_name not in ADMIN_USERNAMES:
        update.message.reply_text(
            "⛔ *Admin Access Required*\n\n"
            "Only admin users can view the list of keys.",
            parse_mode='Markdown'
        )
        return

    # Get the list of valid unused keys
    unused_keys = get_all_valid_keys()
    used_keys_count = len(USED_KEYS)

    if not unused_keys:
        update.message.reply_text(
            "🔑 *No Unused Keys Available*\n\n"
            "There are no unused keys available. Use the /generate_keys command to create new keys.",
            parse_mode='Markdown'
        )
        return

    # Format the response message
    keys_list = "\n".join([f"• `{key}`" for key in unused_keys])

    update.message.reply_text(
        f"🔑 *Available Single-Use Keys*\n\n"
        f"Total available unused keys: {len(unused_keys)}\n"
        f"Total used keys: {used_keys_count}\n\n"
        f"Available keys:\n{keys_list}\n\n"
        f"_These keys can only be used once. After use, they will expire._",
        parse_mode='Markdown'
    )

@check_authentication
def admin_panel(update: Update, context: CallbackContext):
    """Handle the /admin command - only accessible by admins"""
    if update.effective_user is None:
        return

    user_name = update.effective_user.username

    # Check if the user is an admin
    ADMIN_USERNAMES = ["BILLIONAIREBOSS101", "Gazew_07"]

    if user_name not in ADMIN_USERNAMES:
        update.message.reply_text(
            "⛔ *Access Denied*\n\n"
            "Only admin users can access the admin panel.",
            parse_mode='Markdown'
        )
        return

    # Get statistics
    total_users = len(AUTHENTICATED_USERS)
    total_valid_keys = len(VALID_KEYS)
    total_used_keys = len(USED_KEYS)

    # Get authenticated users' usernames
    auth_users_info = []
    for user_id in AUTHENTICATED_USERS:
        try:
            user = context.bot.get_chat(user_id)
            auth_users_info.append(f"@{user.username}" if user.username else f"ID: {user_id}")
        except:
            auth_users_info.append(f"ID: {user_id}")

    # Format lists with simple formatting
    auth_users_list = "\n".join(f"• {user}" for user in auth_users_info)
    available_keys_list = "\n".join(f"• {key}" for key in get_all_valid_keys())
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    admin_message = (
        "🔐 *ADMIN PANEL*\n\n"
        f"📊 *Statistics*\n"
        f"• Total Users: {total_users}\n"
        f"• Valid Keys: {total_valid_keys}\n"
        f"• Used Keys: {total_used_keys}\n\n"
        f"👥 *Authenticated Users*:\n"
        f"{auth_users_list}\n\n"
        f"🔑 *Available Keys*:\n"
        f"{available_keys_list}\n\n"
        f"_Last updated: {current_time}_"
    )

    update.message.reply_text(
        text=admin_message,
        parse_mode='Markdown'
    )

def error_handler(update: Update, context: CallbackContext):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")

    # Send error message to user
    if update and update.effective_message:
        update.effective_message.reply_text(
            "An error occurred while processing your request. Please try again later."
        )