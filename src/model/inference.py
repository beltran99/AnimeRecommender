import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler, StandardScaler, QuantileTransformer

def _get_recommendations(anime_df: pd.DataFrame, ratings_dataset, model, user_id: int) -> list:
    """Generate anime recommendations for our app user, taking into account the ratings added into our platform, the anime dataset to search for similar
    animes to the ones the user has liked and the trained recommender to estimate the ratings of our user on the similar animes.
    Steps:
    1. Get the top k most similar animes to the ones liked by our user (those with a rating equal or higher than 5).
    2. Estimate the ratings that our user would give to the animes we fetched in the previous step.
    3. Sort all the animes based on the estimated ratings
    

    Args:
        anime_df (pd.DataFrame): Anime dataset with info of all the animes
        ratings_dataset (_type_): Ratings dataset with info of user ratings of the animes
        model (_type_): SVD recommender trained on ratings dataset
        user_id (int): User for which we want to generate the recommendations

    Returns:
        list: List of anime recommendations in the form of (anime_id, est_r_ui) tuples
    """
    
    # new user ratings
    new_user_id = ratings_dataset.df.user_id.max()
    new_user_ratings = ratings_dataset.df[ratings_dataset.df.user_id == new_user_id]
    
    # we first get similar animes to the ones liked by the user
    similar_animes = []
    for user_id, anime_id, rating in new_user_ratings.values:
        if rating >= 5:
            partial_result = get_top_k_most_similar_animes(anime_df, anime_id)
            similar_animes.extend(partial_result)  
        
    similar_animes = list(set(similar_animes))
    already_watched = list(new_user_ratings.anime_id.values)
    similar_animes = [x for x in similar_animes if x not in already_watched]
        
    # we now estimate our user ratings on these animes
    results = []
    for anime_id in similar_animes:
        estimated_rating = model.predict(new_user_id, anime_id)
        results.append((anime_id, estimated_rating.est))
        
    sorted_results = sorted(results, key=lambda x: x[1], reverse=True)
    
    return sorted_results
    
    
def get_top_k_most_similar_animes(anime_df: pd.DataFrame, anime_id: int, k: int = 100) -> list:
    """Find the top k most similar animes to a given anime based on several anime features and cosine similarity.

    Args:
        anime_df (pd.DataFrame): Anime dataset with several numerical and categorical features
        anime_id (int): Query anime from which we want to find the similarities
        k (int, optional): Number of similar animes to be found. Defaults to 100.

    Returns:
        list: Top k most similar animes to the given anime
    """
    
    df = anime_df.copy()
    
    df.loc[:, 'episodes'] = StandardScaler().fit_transform(np.array(df.episodes).reshape(-1, 1))
    df.loc[:, 'rating'] = StandardScaler().fit_transform(np.array(df.rating).reshape(-1, 1))
    df.loc[:, 'members'] = QuantileTransformer(output_distribution='normal').fit_transform(np.array(df.members).reshape(-1, 1))
    df.loc[:, 'year'] = StandardScaler().fit_transform(np.array(df.year).reshape(-1, 1))
    
    df = df.drop(columns=['name', 'episodes'])
    df.reset_index(inplace=True)
    
    anime_index = df[df.anime_id==anime_id].index[0]
    
    sims = cosine_similarity(df[df.anime_id==anime_id].values.reshape(1,-1), df)
    result = sims[0]
    result[anime_index] = -1
    
    sorted_indices = np.argsort(-result)
    top_k_indices = sorted_indices[:k]
    top_k_values = result[top_k_indices]
    
    return list(df.loc[top_k_indices].anime_id)
    