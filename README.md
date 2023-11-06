# AnimeRecommender
Anime recommendation system based on Surprise - a Python scikit for recommender systems - made interactive through tkinter-based CustomTkinter library.

![example.png](img/example.png)

## Installation
Clone the repository
```bash
git clone https://github.com/beltran99/AnimeRecommender.git
```

This RecSys is trained on [Kaggle's Anime Recommendations Database](https://www.kaggle.com/datasets/CooperUnion/anime-recommendations-database/data), so the next step consists on downloading it. You can easily download the dataset from your preferred web browser and unzip it on the data folder.

However, you can also download it via command-line through Kaggle’s public API implemented in Python:
- Install the kaggle cli tool and authenticate yourself as indicated in this [tutorial](https://www.kaggle.com/docs/api).
```bash
pip install kaggle
```
- You can check that the tool works correctly by searching for datasets containing the word "anime".
```bash
kaggle datasets list -s "anime"
```
- Create the data subfolder
```bash
mkdir data/external
cd data/external
```
- Download the dataset
```bash
kaggle datasets download -d CooperUnion/anime-recommendations-database
```
- Unzip the downloaded dataset
```bash
unzip anime-recommendations-database.zip
```  

# Functionalities
1. Search for animes
2. Rate the animes you searched for
3. Receive recommendations based on your rating history

## Usage
You can invoke the app with the followning command:
```bash
python3 -m gui.app
```
Then you can use the GUI to search for your favorite animes with the top search bar and add your ratings with the corresponding menus for each of the animes. Once you have rated enough animes, you will be able to receive a recommendation and a button for that purpose will pop up.

## Reference
- [Anime recommendation dataset](https://www.kaggle.com/datasets/CooperUnion/anime-recommendations-database)
- [Surprise recommendation package](https://github.com/NicolasHug/Surprise)
- [CustomTkinter UI library](https://customtkinter.tomschimansky.com/)
- [App Icon by IconsPedia](http://www.iconspedia.com)