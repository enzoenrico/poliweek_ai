# openai usage
# 23/09 -> $0.31 (intro2ai)
#          $6.30 (default / continue)


from dotenv import load_dotenv
from numpy import rec
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

from typing import Any, List, Dict, Union

from langchain.tools import tool
from sqlalchemy import false

# loading credentials
load_dotenv()
client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
redirect_uri = "http://localhost:8888/callback"

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope="playlist-modify-public user-read-playback-state user-modify-playback-state app-remote-control playlist-read-private user-top-read",
    )
)


@tool
def get_user():
    """
    Get the current user's profile information.

    :return: A dictionary containing the user's profile information.
    """

    return sp.me()


@tool
def get_recommended_by_genre(genres: List[str]) -> List[Dict]:
    """
    Get track recommendations based on the provided genres.

    :param genres: A list of genre names to seed the recommendations.
    :return: A list of recommended tracks.
    """
    recommends = sp.recommendations(seed_genres=genres, limit=10)
    if recommends:
        return recommends["tracks"]
    return []


# @tool
# def get_recommended_by_artist(artist_id: str) -> Union[List[Dict[str, str]], None]:
#     """
#     Get artist recommendations based on the provided artist ID.

#     :param artist_id: The Spotify artist ID to seed the recommendation.
#     :return A list of recommended artists or None if no recommendations are available.
#     """
#     recomends = sp.artist_related_artists(artist_id=artist_id)
#     if recomends and "artists" in recomends:
#         return recomends["artists"]
#     return None


@tool
def search_by_track_name(track_name: str) -> Union[List[Dict[str, Any]], None]:
    """
    Search for tracks by their name.

    :param track_name: The name of the track to search for.
    :return: A list of dictionaries, each representing a track if found, otherwise None.
    """
    res = sp.search(q=track_name, type="track", limit=10)
    if res:
        return res["tracks"]["items"]
    return None


@tool
def get_songs_from_artist(artist_id: str):
    """
    Get top tracks from a specific artist.

    :param artist_id: The Spotify ID of the artist.
    :return: A list of track dictionaries representing the artist's top tracks.
    """

    recommendations = sp.artist_top_tracks(artist_id)
    print("recommendations:")
    print(recommendations)
    if recommendations:
        return recommendations["tracks"]


@tool
def select_url_from_track(track: Dict[str, str]):
    """
    Select a track from a list of tracks and return its URI.
    """
    if "spotify" in track:
        return track["spotify"]
    if "external_urls" in track:
        if "spotify" in track["external_urls"]:
            return track["external_urls"]["spotify"]



#TEST THIS !!!!!
@tool
def get_artist_albums(artist_id: str) -> Union[List[Dict[str, Any]], None]:
    """
    Retrieve albums from a specific artist.

    :param artist_id: The Spotify ID of the artist.
    :return: A list of albums dictionaries or None if no albums are found.
    """
    albums = sp.artist_albums(artist_id)
    if albums:
        return albums.get("items", None)
    return None

@tool
def get_songs_from_album(album_id: str) -> Union[List[Dict[str, Any]], None]:
    """
    Retrieve tracks from a specific album.

    :param album_id: The Spotify ID of the album.
    :return: A list of track dictionaries if found, otherwise None.
    """
    tracks = sp.album_tracks(album_id) 
    if tracks:
        return tracks.get("items", None)
    return None


# remove on tools
# consumes way too many tokens
# @tool
# def select_urls_from_query(tracks: List[Any]):
#     """
#     Select multiple tracks from a list of tracks and return their URIs.

#     :param tracks: A list of track dictionaries.
#     :return: A list of Spotify URIs for the selected tracks.
#     """

#     res = []
#     for track in tracks:
#         res.append(track["spotify"])
#     return res


@tool
def get_artist_id(artist_name: str) -> Union[str, None]:
    """
    Get the Spotify artist ID for a given artist name.

    :param artist_name: The name of the artist to search for.
    :return: The artist's Spotify ID as a string, or None if the artist is not found.
    """
    results = sp.search(q="artist:" + artist_name, type="artist")
    if results:
        items = results["artists"]["items"]
        if len(items) > 0:
            return items[0]["id"]
        else:
            return None
    return None


# @tool
# def get_song_lyrics(song_id:str):
# idk how tf to implement this
# search again when i got wifi


# don't use this, consumes WAAAY too many tokens
# @tool
# def recommendation_playlist(tracklist: List[str]) -> str:
#     """
#     Create a recommendation playlist with the provided tracklist.

#     :param tracklist: A list of Spotify track URIs to be added to the playlist.
#     :return: The Spotify ID of the created playlist.
#     """
#     print('tracklist')
#     print(tracklist)
#     pl = sp.user_playlist_create(
#         sp.me()["id"],
#         "Recommended Songs",
#         public=True,
#         description="Songs recommended by your AI DJ",
#     )
#     print(pl["id"])
#     sp.playlist_add_items(playlist_id=pl["id"], items=tracklist)
#     return pl["id"]


# @tool
# def parse_into_playlist(items: List[Dict[str, Any]]) -> List[str]:
#     """
#     Parse a list of items into a list of Spotify track URIs.

#     :param items: A list of dictionaries, each containing track information.
#     :return: A list of Spotify track URIs.
#     """
#     res = []
#     for item in items:
#         if "uri" in item:
#             res.append(item["uri"])
#     return res


@tool
def play_song_on_device(songs: List[str]):
    """
    Play a list of songs on the user's active Spotify device.

    :param songs: A list of Spotify track URIs to be played.
    :return: True if the playback starts successfully, False otherwise.
    """

    try:
        sp.start_playback(uris=songs)
        return True
    except Exception as e:
        print(e)
        return false
