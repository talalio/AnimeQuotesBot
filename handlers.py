import requests
from random import randint
from telegram import Update, ParseMode
from telegram.ext import Updater, CallbackContext

USER_AGENT = 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36'

def get_character_picture(character) -> str:
    """ Retrive a random character image """
    results = None
    try:
        parameters = {'q': character, 'limit': 3}
        query = requests.get("https://api.jikan.moe/v3/search/character", params=parameters, headers={'User-Agent': USER_AGENT}, timeout=10)
        if query.status_code == 200:
            results = query.json()['results'][0]
    except:
        pass
    picture_url = None
    if results:
        character_id = results['mal_id']
        try:
            pictures_list = requests.get(f'https://api.jikan.moe/v3/character/{character_id}/pictures', headers={'User-Agent': USER_AGENT}, timeout=10).json()['pictures']
            picture_url = pictures_list[randint(0, len(pictures_list)-1)]['large']
        except:
            pass
    return picture_url

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
        context.bot.send_message(chat_id=id, text="Sorry, no quotes found!")
        return
    data = quotes
    quote = data['quote']
    character = data['character']
    anime = data['anime']
    picture = get_character_picture(character)
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
    try:
        parameters = {'name': character}
        query = requests.get("https://animechan.vercel.app/api/quotes/character", headers={'User-Agent': USER_AGENT}, params=parameters)
        if valid_query(query):
            quote = query.json()[randint(0,len(quote)-1)]
    except Exception as e:
    	print(e)
    chat_id = update.effective_chat.id
    send_quote(chat_id, context, quote)

def anime_quote(update: Update, context: CallbackContext) -> None:
    """ Get quote by anime title """
    anime = ' '.join(context.args)
    quote = None
    try:
        parameters = {'title': anime}
        query = requests.get("https://animechan.vercel.app/api/quotes/anime", headers={'User-Agent': USER_AGENT}, params=parameters)
        if valid_query(query):
            quote = query.json()[randint(0,len(quote)-1)]
    except Exception as e:
        print(e)
    chat_id = update.effective_chat.id
    send_quote(chat_id, context, quote)

def random_quote(update: Update, context: CallbackContext) -> None:
    """ fetch and send a random quote """
    quote = None
    query = requests.get('https://animechan.vercel.app/api/random', headers={'User-Agent': USER_AGENT})
    if valid_query(query):
        quote = query.json()
    chat_id = update.effective_chat.id
    send_quote(chat_id, context, quote)

def unknown_commands(update: Update, context: CallbackContext) -> None:
    """ Return a message for unknown commands """
    update.message.reply_text("Unknown command!!")

def valid_query(query) -> bool:
    if query.status_code == 200:
        return True
    return False
