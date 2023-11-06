import pandas as pd
import numpy as np
import html
from surprise import Reader, Dataset

from pathlib import Path
abs_path = Path(__file__).parent

def preprocess_anime_data(df: pd.DataFrame) -> pd.DataFrame:
    """Preprocess the raw anime dataset and make it suitable for training/inference.

    Args:
        df (pd.DataFrame): Dataframe to be processed

    Returns:
        pd.DataFrame: Processed dataframe
    """
    # convert name to unicode
    df['name'] = df.name.map(lambda x: html.unescape(x))

    # get genre dummies
    genre_dummies = df['genre'].str.get_dummies(', ')
    genre_dummies = genre_dummies.add_prefix('genre_')
    genre_dummies.rename(columns=lambda x: x.replace(" ", "_"), inplace=True)
    df = pd.concat([df, genre_dummies], axis=1)

    # remove unappropiate genres
    mask = (df.genre_Hentai == 0) & (df.genre_Ecchi == 0) & (df.genre_Harem == 0)
    df = df[mask]
    df.drop(columns=['genre', 'genre_Hentai', 'genre_Ecchi', 'genre_Harem'], inplace=True)

    # keep only movies or TV series
    mask = (df.type == 'Movie') | (df.type == 'TV')
    df = df[mask]

    # get anime type dummies
    type_dummies = pd.get_dummies(df.type, prefix='type')
    df = pd.concat([df, type_dummies], axis=1)
    df.drop(columns=['type'], inplace=True)

    # concat additional anime metadata - release date
    release_dates = pd.read_csv(abs_path / ('../../data/raw/anime_dates.csv'))
    df = df.merge(release_dates, on='anime_id')

    # set anime_id as df index
    df.set_index('anime_id', drop=False, inplace=True)
    
    # anime metadata - update episodes
    episode_data = pd.read_csv(abs_path / ('../../data/raw/anime_episodes.csv'))
    episode_data.set_index('anime_id', inplace=True)
    df.update(episode_data)
    
    # create new stillAiring feature based on episodes
    df['stillAiring'] = df.episodes.map(lambda x: True if x == 'Unknown' else False)

    # cast episodes to float
    df['episodes'] = df.episodes.replace('Unknown', np.nan)
    df['episodes'] = df.episodes.astype("float64")
    
    # remove outliers - animes with too much episodes
    df = df[(df.episodes <= 500) | (df.index == 2471) | (df.episodes.isna())]
    
    # anime metadata - update rating
    scores_data = pd.read_csv(abs_path / ('../../data/raw/anime_scores.csv'))
    scores_data.set_index('anime_id', inplace=True)
    scores_data.rename(columns={'scores': 'rating'}, inplace=True)
    df.update(scores_data)
    
    # remove rows without mean rating or release date
    df.dropna(subset=['rating', 'year'], inplace=True)
    
    df.reset_index(drop=True, inplace=True)

    return df


def preprocess_ratings_data(ratings: pd.DataFrame, anime: pd.DataFrame):
    """Preprocess the raw ratings dataset and make it suitable for training/inference.

    Args:
        ratings (pd.DataFrame): Raw ratings dataframe
        anime (pd.DataFrame): Processed anime dataframe

    Returns:
        _type_: Ratings Surprise-dataset
    """
    ratings = ratings[ratings.rating != -1]
    if anime.index.name == "anime_id":
        ratings = ratings[ratings.anime_id.isin(anime.index)]
    else:
        ratings = ratings[ratings.anime_id.isin(anime.anime_id)]
    
    reader = Reader(rating_scale=(1,10))
    ratings_dataset = Dataset(reader)
    ratings_dataset = ratings_dataset.load_from_df(ratings, reader)

    return ratings_dataset