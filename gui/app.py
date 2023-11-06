import tkinter
from typing import Optional, Tuple, Union
import customtkinter
import pandas as pd
from PIL import Image, ImageTk
import ratelimit
import io
import time
from pathlib import Path
abs_path = Path(__file__).parent

from src.dataset.preprocessing import preprocess_anime_data, preprocess_ratings_data
from src.dataset.download_data import get_anime_metadata
from src.model.train import simple_train
from src.model.inference import _get_recommendations

IMAGE_WIDTH = 250
IMAGE_HEIGHT = 250

customtkinter.set_appearance_mode('system')
customtkinter.set_default_color_theme('dark-blue')

class App(customtkinter.CTk):
    """Recommender application that along with a GUI allows you to:
        1. Search for animes
        2. Rate the animes you searched for
        3. Receive recommendations based on your rating history

    Args:
        customtkinter (_type_): App window
    """
    def __init__(self):
        """Initializes the gui application
        """
        super().__init__()
        
        anime_df = pd.read_csv(abs_path / ('../data/external/anime.csv'))
        anime_df = preprocess_anime_data(anime_df)
        self.anime_df = anime_df

        ratings_df = pd.read_csv(abs_path / ('../data/external/rating.csv'))
        self.ratings_df = ratings_df
        
        self.new_ratings = {}
        self.isRecommendationsActive = False
        
        self.title('Anime Recommender')
        self.geometry('500x350')
        self.wm_iconphoto(True, ImageTk.PhotoImage(file=(abs_path / 'One-Piece-anime.ico')))
        
        self.top_frame = customtkinter.CTkFrame(master=self)
        self.top_frame.pack(pady=20, padx=50, fill="none", expand=False)

        self.search_label = customtkinter.CTkLabel(master=self.top_frame, text="Search for anime", font=("Roboto", 24))
        self.search_label.grid(row=0, column=0, padx=(50, 0), pady=12)

        self.search_entry = customtkinter.CTkEntry(master=self.top_frame, placeholder_text="Search")
        self.search_entry.grid(row=1, column=0, padx=(10, 0), pady=12)

        self.search_button = customtkinter.CTkButton(master=self.top_frame, text="Search", command=self.search)
        self.search_button.grid(row=1, column=1, padx=(2, 25), pady=(12, 12))
        
        self.bottom_frame = customtkinter.CTkScrollableFrame(master=self)
        self.bottom_frame.pack(pady=5, padx=50, fill="both", expand=True)

    
    def search(self):
        """Search functionality that fetches animes based on the coincidence of the introduced query and the anime names.
        It displays the search results in rows ordered from most to least popular, displaying: anime id, name, cover image, synopsis and the corresponding widgets add their ratings.
        """
        
        self.search_widgets = []
        
        for widget in self.bottom_frame.winfo_children():
            widget.destroy()
    
        # perform query
        query = self.search_entry.get().lower()
        search_result = self.anime_df[self.anime_df['name'].str.lower().str.contains(query)]
        search_result.sort_values(by="members", ascending=False)
        
        grid_row = 0
        api_counter = 0
        for i, df_row in search_result.iterrows():
            anime_id = df_row['anime_id']
            anime_name = df_row['name']

            if api_counter == 3:
                time.sleep(1.5)
                api_counter = 0
            synopsis, cover_image = get_anime_metadata(anime_id)
            api_counter += 1
            
            id_label = customtkinter.CTkLabel(master=self.bottom_frame, text=anime_id, font=("Roboto", 16), wraplength=150)
            id_label.grid(row=grid_row, column=0, padx=(10, 0), pady=12)
            
            name_label = customtkinter.CTkLabel(master=self.bottom_frame, text=anime_name, font=("Roboto", 20), wraplength=250)
            name_label.grid(row=grid_row, column=1, padx=(5, 0), pady=12)
            
            image = Image.open(cover_image)
            photo = customtkinter.CTkImage(light_image=image, size=(IMAGE_WIDTH , IMAGE_HEIGHT))
            cover_image_label = customtkinter.CTkLabel(master=self.bottom_frame, image=photo, text='')
            cover_image_label.grid(row=grid_row, column=2, padx=(10, 0), pady=12)
            
            synopsis_label = customtkinter.CTkLabel(master=self.bottom_frame, text=synopsis, font=("Roboto", 14), wraplength=750)
            synopsis_label.grid(row=grid_row, column=3, padx=(10, 0), pady=12)
            
            values = list(map(str, range(1,11)))
            rating_menu = customtkinter.CTkOptionMenu(master=self.bottom_frame, values=values)
            rating_menu.grid(row=grid_row, column=4, padx=(10, 0), pady=12)
            
            rating_button = customtkinter.CTkButton(master=self.bottom_frame, text='Save rating')
            rating_button.grid(row=grid_row, column=5, padx=(10, 0), pady=12)
            rating_button.bind("<Button-1>", self.save_rating)
            
            self.search_widgets.append([id_label, rating_menu, rating_button])
            
            grid_row += 1
        
        
    def save_rating(self, event):
        """Event function that saves the user new rating of a given anime. When the Save rating button is clicked, the rating from the Option Menu of the same anime row is saved.
        This function also checks if there is any positive review saved by the user and in that case makes the recommend functionality available.

        Args:
            event (_type_): Mouse-clicking event that raises the function call
        """
        
        button_name = str(event.widget)
        button_name = button_name.replace(".!ctkcanvas", "").replace(".!label", "")
        
        for id_label, optionMenu, button in self.search_widgets:
            if str(button) == button_name:
                anime_id = id_label.cget('text')
                rating = int(optionMenu.get())
                
                # print(f"Rating for anime {anime_id} is {rating}")                        
                    
                self.new_ratings[anime_id] = rating
                
                for anime_id, rating in self.new_ratings.items():
                    if rating >= 5 and not self.isRecommendationsActive:
                        recommendation_button = customtkinter.CTkButton(master=self.top_frame, text='Recommend me something', command=self.make_recommendations)
                        recommendation_button.grid(row=1, column=2, padx=(25, 15), pady=(12, 12))
                        
                        self.isRecommendationsActive = True
                        
                        break
                    
                break    
        
        
    def make_recommendations(self):
        """This function retrieves all of the user's ratings, gets some recommendations based on them and displays them from most to least recommended.
        """
        
        for widget in self.bottom_frame.winfo_children():
            widget.destroy()
            
        new_ratings_df = self.ratings_df.copy()
        
        # add new ratings from new user
        new_user = self.ratings_df.user_id.max() + 1
        for anime_id, rating in self.new_ratings.items():
            new_row_df = pd.DataFrame({'user_id': [new_user], 'anime_id': [anime_id], 'rating': [rating]})
            new_ratings_df = pd.concat([new_ratings_df, new_row_df], ignore_index=True)
            
        ratings_dataset = preprocess_ratings_data(new_ratings_df, self.anime_df)
        
        model = simple_train(ratings_dataset)
        
        recommendations = _get_recommendations(self.anime_df, ratings_dataset, model, new_user)
        top_10_recommendations = recommendations[:10]
        
        api_counter = 0
        for i, (anime_id, est_rating) in enumerate(top_10_recommendations):
            anime_name = self.anime_df[self.anime_df.anime_id == anime_id].name.values[0]
            # print(i, anime_id, anime_name, est_rating)
            
            if api_counter == 3:
                time.sleep(1.5)
                api_counter = 0
            synopsis, cover_image = get_anime_metadata(anime_id)
            api_counter += 1
            
            name_label = customtkinter.CTkLabel(master=self.bottom_frame, text=anime_name, font=("Roboto", 20), wraplength=350)
            name_label.grid(row=i, column=0, padx=(5, 0), pady=12)
            
            image = Image.open(cover_image)
            photo = customtkinter.CTkImage(light_image=image, size=(IMAGE_WIDTH , IMAGE_HEIGHT))
            cover_image_label = customtkinter.CTkLabel(master=self.bottom_frame, image=photo, text='')
            cover_image_label.grid(row=i, column=1, padx=(10, 0), pady=12)
            
            synopsis_label = customtkinter.CTkLabel(master=self.bottom_frame, text=synopsis, font=("Roboto", 14), wraplength=850)
            synopsis_label.grid(row=i, column=2, padx=(10, 0), pady=12)
            

if __name__ == "__main__":
    app = App()
    app.mainloop()