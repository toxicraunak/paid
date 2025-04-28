import threading
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
logger.info("Starting Binary Trading Signals Bot application")

from app import app, run_flask_app, start_bot_thread

# This app object is used by Gunicorn for the 'Start application' workflow
# Start the bot in a separate thread
try:
    start_bot_thread()
    logger.info("Bot thread started successfully")
except Exception as e:
    logger.error(f"Error starting bot thread: {e}")

if __name__ == "__main__":
    logger.info("Running Flask app in the main thread")
    # Run the Flask web app in the main thread
    run_flask_app()
