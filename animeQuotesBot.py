import logging
import os
from handlers import *
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

logging.basicConfig(
	format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

BOT_TOKEN = os.environ.get('BOT_TOKEN')

def main() -> None:
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start, run_async=True))
    dispatcher.add_handler(CommandHandler('help', help_handler, run_async=True))
    dispatcher.add_handler(CommandHandler('aquote', anime_quote, run_async=True))
    dispatcher.add_handler(CommandHandler('cquote', character_quote, run_async=True))
    dispatcher.add_handler(CommandHandler('rquote', random_quote, run_async=True))

	# Add unknown messages handler
    dispatcher.add_handler(MessageHandler(Filters.command, unknown_commands, run_async=True ))

    # Add error handlers
    dispatcher.add_error_handler(error_handler)

    PORT = int(os.environ.get('PORT', '8443'))
    # add handlers
    updater.start_webhook(
    	listen="0.0.0.0",
        port=int(PORT),
        url_path=BOT_TOKEN,
        webhook_url="https://yourapp.herokuapp.com/" + BOT_TOKEN
    )
    updater.idle()

if __name__=='__main__':
    main()
