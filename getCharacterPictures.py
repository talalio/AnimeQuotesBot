import requests
import json
import urllib
import logging
from random import randint

logging.basicConfig(
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

def get_character_picture(character) -> str:
    """ Retrive a random character image """
    results = None
    try:
        query = requests.get(f"https://api.jikan.moe/v3/search/character?q={urllib.parse.quote_plus(character)}&limit=2", timeout=10)
        if query.status_code == 200:
            results = query.json()['results'][0]
    except:
        pass
    picture_url = None
    if results:
        character_id = results['mal_id']
        try:
            pictures_list = requests.get(f'https://api.jikan.moe/v3/character/{character_id}/pictures', timeout=10).json()['pictures']
            picture_url = pictures_list[randint(0, len(pictures_list))]['large']
        except:
            pass
    return picture_url
