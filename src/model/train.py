import pandas as pd

from surprise.model_selection import train_test_split
from surprise.prediction_algorithms import SVD
from surprise import accuracy, dump

from pathlib import Path
abs_path = Path(__file__).parent
    
from src.dataset.preprocessing import preprocess_anime_data, preprocess_ratings_data

def _train(model):
    """Train a Surprise model on the anime dataset and evaluate it.

    Args:
        model (_type_): A Surprise model

    Returns:
        _type_: Fitted model RMSE on test set
    """
    anime_df = pd.read_csv(abs_path / ('../../data/external/anime.csv'))
    anime_df = preprocess_anime_data(anime_df)
    
    anime_df.set_index('anime_id', drop=True, inplace=True)

    ratings_df = pd.read_csv(abs_path / ('../../data/external/rating.csv'))
    ratings_dataset = preprocess_ratings_data(ratings_df, anime_df)
    
    trainset, testset = train_test_split(ratings_dataset, test_size=0.2, random_state=5)
    
    model.fit(trainset)
    
    predictions = model.test(testset)
    
    metrics = accuracy.rmse(predictions, verbose=False)
    print(metrics)
    
    return metrics
    

def simple_train(dataset):
    """Train a SVD model from Surprise on a given dataset

    Args:
        dataset (_type_): Surprise dataset for recommendation

    Returns:
        _type_: Fitted model
    """

    trainset = dataset.build_full_trainset()
    
    model = SVD()
    model.fit(trainset)
    
    return model


def _grid_search(gs):
    """Perform a grid search on a Surprise model with a recommendation dataset

    Args:
        gs (_type_): GridSearchCV Surprise object

    Returns:
        _type_: Fitted grid search object
    """
    anime_df = pd.read_csv(abs_path / ('../../data/external/anime.csv'))
    anime_df = preprocess_anime_data(anime_df)
    
    anime_df.set_index('anime_id', drop=True, inplace=True)

    ratings_df = pd.read_csv(abs_path / ('../../data/external/rating.csv'))
    ratings_dataset = preprocess_ratings_data(ratings_df, anime_df)
    
    gs.fit(ratings_dataset)
    algo = gs.best_estimator["rmse"]
    
    return gs