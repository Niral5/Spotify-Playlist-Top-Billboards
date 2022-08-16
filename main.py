from datetime import date
from re import search

import spotipy
import os
import requests
from spotipy.oauth2 import SpotifyClientCredentials
from bs4 import BeautifulSoup

spotify_client_id = "75b40848e5524eacade7bd7c048606c7"
spotify_client_secret = "2e5a2f562d2d435ea011ca52df8809c8"
SPOTIPY_REDIRECT_URI = "http://example.com"


# --------------------------------Asking Date---------------------------------#
def which_date():
    input_date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")
    return input_date


# # -----------------------Give Error if wrong date format-----------------------#
valid_date = ""
while True:
    try:
        valid_date = date.fromisoformat(which_date())
    except ValueError:
        print("error please type it in the correct format")
        continue
    break

print(valid_date)

# --------------------------------Getting Song List from Billboards--------------#
response = requests.get(f"https://www.billboard.com/charts/hot-100/{valid_date}/")
billboards_page = response.text

soup = BeautifulSoup(billboards_page, "html.parser")
page = soup.body.main

song_list = [songs.getText().strip().replace("'", "").replace("!", "") for songs in page.select(selector="li ul li h3")]
print(song_list)
print(len(song_list))

artist_list = []
for artists in page.select(selector="ul li ul li span"):
    artist = artists.getText().strip().split(" Featuring")[0].split(" Duet")[0].split("&")[0].split("And")[0]
    if not artist == "-" and not artist.isnumeric():
        if search(",", artist):
            updated_artist = artist.partition(",")[0]
            artist_list.append(updated_artist)
        else:
            artist_list.append(artist)

print(artist_list)
print(len(artist_list))

#  ------------------------Getting Spotipy Authorization--------------------------------#
scope = 'user-read-currently-playing'

oauth_object = spotipy.SpotifyOAuth(client_id=spotify_client_id,
                                    client_secret=spotify_client_secret,
                                    redirect_uri=SPOTIPY_REDIRECT_URI,
                                    scope="playlist-modify-private",
                                    cache_path=".cache.txt")

token_dict = oauth_object.get_access_token()
token = token_dict['access_token']

spotify_object = spotipy.Spotify(auth=token)

user_id = (spotify_object.current_user()["id"])
user_name = spotify_object.current_user()["display_name"]

song_urls = []

# ---------------Use To test Individual-------------#
# "track: {Dark Horse} year: {2014-02-12}"
# track = "Summer"
# artist = "Calvin Harris"
# playlist_name = input("Name of Playlist")
# playlist_description = "Playlist from the top Billboard songs from a specified date"

# result = spotify_object.search(q=f"track:{track} artist:{artist}", type="track")["tracks"]["items"]
# print(result)

for song, artist in zip(song_list, artist_list):
    items = spotify_object.search(q=f"track: {song} artist: {artist}", type="track")["tracks"]["items"]
    if len(items) > 0:
        song_urls.append(items[0]["uri"])

playlist_id = spotify_object.user_playlist_create(user=user_id, name=f"{valid_date} Billboard 100", public=False)["id"]

spotify_object.playlist_add_items(playlist_id=playlist_id, items=song_urls)
