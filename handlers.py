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

def send_quote(id: int, context: CallbackContext, quotes: dict, job = None) -> None:
    """ send a quote """
    if not quotes:
        update.message.reply_text("Sorry, no quotes found!")
        return
    data = quotes
    quote = data['quote']
    character = data['character']
    anime = data['anime']
    picture = getCharacterPictures.get_character_picture(character)
    if picture:
        context.bot.send_photo(
            chat_id=id,
            photo=f'{picture}',
            caption=f"\"<b><i>{quote}</i></b>\"\n- <i>{character}</i> \n- <i>{anime}</i>",
            parse_mode=ParseMode.HTML
        )
    else:
        context.bot.send_message(
            chat_id=id,
            text=f"\"<b><i>{quote}</i></b>\"\n- <i>{character}</i> \n- <i>{anime}</i>",
            parse_mode=ParseMode.HTML
        )
    return

def character_quote(update: Update, context: CallbackContext) -> None:
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
    chat_id = update.effective_chat.id
    send_quote(chat_id, context, quote)

def anime_quote(update: Update, context: CallbackContext) -> None:
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
    chat_id = update.effective_chat.id
    send_quote(chat_id, context, quote)

def random_quote(update: Update, context: CallbackContext) -> None:
    """ fetch and send a random quote """
    data = requests.get('https://animechan.vercel.app/api/random').json()
    chat_id = update.effective_chat.id
    send_quote(chat_id, context, quote)

def unknown_commands(update: Update, context: CallbackContext) -> None:
    """ Return a message for unknown commands """
    update.message.reply_text("Unknown command!!")
