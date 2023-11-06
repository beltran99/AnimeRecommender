import io
import requests
from jikanpy import Jikan
from typing import Tuple

def get_anime_data(anime_id: int, variables: list) -> list:
    """Query Jikan API to ask for the release date, title in english, number of episodes or average score of a given anime.

    Args:
        anime_id (int): Anime to query about
        variables (list): List of fields to query about. Possible fields are: "year", "title_english", "episodes", "score"

    Returns:
        list: Anime data received from the API
    """
    jikan = Jikan()
    data = []
    try:
        anime_info = jikan.anime(anime_id)
        for variable_name in variables:
            if variable_name == 'year':
                try:
                    year = anime_info['data']['year']
                    if year is None:
                        year = anime_info['data']['aired']['prop']['from']['year']
                    data.append(year)
                except Exception as e:
                    print(f"There was an error when trying to get the year of release from anime with id {anime_id}")
                    print(e)
                    data.append(None)
            else:
                try:
                    var_data = anime_info['data'][variable_name]
                    data.append(var_data)
                except Exception as e:
                    print(f"There was an error when trying to get {variable_name} data from anime with id {anime_id}")
                    print(e)
                    data.append(None)
    except Exception as e:
        print(f"There was an error when trying to get information from anime with id {anime_id}")
        print(e)
    
    return data

def _get_anime_data(anime_id: int) -> Tuple[str, float]:
    """Query Jikan API to obtain the title in english and release date of a given anime.

    Args:
        anime_id (int): Anime to query about

    Returns:
        Tuple[str, float]: Title in english and release date of the anime
    """
    jikan = Jikan()

    title_english = None
    synopsis = None
    year = None
    
    try:
        anime_info = jikan.anime(anime_id)
        try:
            title_english = anime_info['data']['title_english']
        except Exception as e:
            print(f"There was an error when trying to get the title in english from anime with id {anime_id}")
            print(e)        
        try:
            year = anime_info['data']['year']
            if year is None:
                year = anime_info['data']['aired']['prop']['from']['year']
        except Exception as e:
            print(f"There was an error when trying to get the year of release from anime with id {anime_id}")
            print(e)      
    
    except Exception as e:
        print(f"There was an error when trying to get information from anime with id {anime_id}")
        print(e)
    
    return title_english, year

def get_anime_episodes(anime_id: int) -> float:
    """Query Jikan API to obtain the number of episodes of a given anime.

    Args:
        anime_id (int): Anime to query about

    Returns:
        float: Number of episodes of the anime
    """
    
    jikan = Jikan()
    nb_episodes = None

    try:
        anime_info = jikan.anime(anime_id)
        try:
            nb_episodes = anime_info['data']['episodes']
        except Exception as e:
            print(f"There was an error when trying to get the number of episodes from anime with id {anime_id}")
            print(e)   
    
    except Exception as e:
        print(f"There was an error when trying to get information from anime with id {anime_id}")
        print(e)
    
    return nb_episodes

def get_anime_metadata(anime_id: int) -> Tuple[str, io.BytesIO]:
    """Query Jikan API to obtain the synopsis and cover image of a given anime.

    Args:
        anime_id (int): Anime to query about

    Returns:
        Tuple[str, io.BytesIO]: Synopsis and cover image of the anime
    """
    
    jikan = Jikan()

    synopsis = None
    cover_image = None
    
    try:
        anime_info = jikan.anime(anime_id)

        try:
            synopsis = anime_info['data']['synopsis']
        except Exception as e:
            print(f"There was an error when trying to get the synopsis from anime with id {anime_id}")
            print(e)
        
        try:
            cover_image_url = anime_info['data']['images']['jpg']['large_image_url']
            response = requests.get(cover_image_url)
            cover_image = io.BytesIO(response.content)
        except Exception as e:
            print(f"There was an error when trying to get the cover image from anime with id {anime_id}")
            print(e)
    
    except Exception as e:
        print(f"There was an error when trying to get information from anime with id {anime_id}")
        print(e)

    return synopsis, cover_image