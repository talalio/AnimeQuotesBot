import html
import json
import traceback
import logging
import requests
import getCharacterPictures
import urllib
from random import randint
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from multipledispatch import dispatch

logging.basicConfig(
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Hi! use /help to know the commands.")

def help_handler(update: Update, context: CallbackContext):
    """ Display help message """
    message = (
        '/rquote - to get a random quote\n'
        '/aquote <anime> - to get a quote by anime title\n'
        '/cquote <character> - to get a quote by character name\n'
        '/help - to display this message\n'
        )
    update.message.reply_text(message)

def send_quote(update: Update, context: CallbackContext, quotes: dict, job = None):
    """ send a quote """
    if not quotes:
        update.message.reply_text("Sorry, no quotes found!")
        return
    data = quotes
    quote = data['quote']
    character = data['character']
    anime = data['anime']
    picture = getCharacterPictures.get_character_picture(character)
    if not job:
        if picture:
            context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=f'{picture}',
                caption=f"\"<b><i>{quote}</i></b>\"\n- <i>{character}</i> \n- <i>{anime}</i>",
                parse_mode=ParseMode.HTML
            )
        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"\"<b><i>{quote}</i></b>\"\n- <i>{character}</i> \n- <i>{anime}</i>",
                parse_mode=ParseMode.HTML
            )
        return

    job = context.job
    picture = getCharacterPictures.get_character_picture(character)
    message = f"\"<b><i>{quote}</i></b>\"\n- <i>{character}</i> \n- <i>{anime}</i>"
    if picture:
        message = f"\"<b><i>{quote}</i></b>\"\n- <i>{character}</i> \n- <i>{anime}</i>"
        context.bot.send_photo(
            job.context,
            photo=f'{picture}',
            caption=message,
            parse_mode=ParseMode.HTML
        )
        return

    try:
        context.bot.send_message(
            job.context,
            text=message,
            parse_mode=ParseMode.HTML
        )
    except(TypeError):
        logger.error(msg=f"TypeError while sending a queued message without a photo")

def character_quote(update: Update, context: CallbackContext):
    """ Get a quote by a spacific character """
    character = ' '.join(context.args)
    quote = None
    if len(character) < 2:
        update.message.reply_text("character name must be more then 4 characters!")
        return
    try:
    	quote = requests.get(f"https://animechan.vercel.app/api/quotes/character?name={urllib.parse.quote_plus(character)}").json()
    	quote = quote[randint(0,len(quote)-1)]
    except:
    	quote = None

    send_quote(update, context, quote)

def anime_quote(update: Update, context: CallbackContext):
    """ Get quote by anime title """
    anime = ' '.join(context.args)
    if len(anime) < 3:
        update.message.reply_text("anime title must be more than 2 characters")
        return
    try:
        quote = requests.get(f"https://animechan.vercel.app/api/quotes/anime?title={urllib.parse.quote_plus(anime)}").json()
        quote = quote[randint(0,len(quote)-1)]
    except:
        quote = None
    send_quote(update, context, quote)

@dispatch(Update, CallbackContext)
def random_quote(update: Update, context: CallbackContext) -> None:
    """ fetch and send a random quote """
    data = requests.get('https://animechan.vercel.app/api/random').json()
    send_quote(update, context, data)

def remove_job_if_exists(name: str, context: CallbackContext) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True

def unknown_commands(update: Update, context: CallbackContext):
    """ Return a message for unknown commands """
    update.message.reply_text("Unknown command!!")
