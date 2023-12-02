#%% Imports
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

import requests
import os
import sys

# Need to later rebuild the authentification to work with JSON files that contain API keys etc.
# for others to use the script (provide example JSONs in documentation)

"""
babobusyt@gmail.com
Heute-Abend-Um-6
"""
#%% Spotify related functions  
def authenticate_spotify():
    """
    Uses environment variables to gain access to Spotify API
    
    Environment variables:
    SPOTIPY_CLIENT_ID
    SPOTIPY_CLIENT_SECRET
    SPOTIPY_REDIRECT_URI

    All found on the Spotify Developers Dashboard:
    https://developer.spotify.com/dashboard/20f128d8178c4ba3b89f4adf4e495b44/settings
    
    Returns:
        spotipy.Spotify instance that interacts with Spotify API
    """
    spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
    return spotify

def get_spotify_playlist_info(spotify, playlist_link):
    """
    Interacts with Spotify API to get all playlist info.
    Doesn't work with album links.

    Args:
        playlist_link (str): Link to playlist
        spotify: Spotify API Client

    Returns:
        str: Playlist Name
        dict: Tracklist with Title and Artists
    """    
    playlist_id = playlist_link.split('/')[-1].split('?')[0]
    playlist_info = spotify.playlist(playlist_id) # All Playlist info in here
    
    playlist_name = playlist_info['name'] # Playlist Name to create YT Playlist with same name
    
    tracks = playlist_info['tracks']['items']
    tracklist = {}
    for track in tracks:
        track_info = track['track']
        # print(track_info['artists'])
        title = track_info['name']
        artists = [artist['name'] for artist in track_info['artists']]
        # duration_ms = track_info['duration_ms']
        
        tracklist[title] = artists # Tracklist with key: Song Name and value: List of Artists
        
    return playlist_name, tracklist

#%% Youtube related functions
def build_youtube_api_client():
    """Authorizes access to a Youtube Account

    Returns:
        youtube_api_client: Authorized YouTube API client object.
    """
    # Load the OAuth 2.0 credentials from a file
    flow = InstalledAppFlow.from_client_secrets_file(
        "client_secrets.json",
        scopes=["https://www.googleapis.com/auth/youtube.force-ssl"]
    )
    # Prompt the user to authorize the application
    credentials = flow.run_local_server()

    # Build the YouTube API client
    youtube = build("youtube", "v3", credentials=credentials)
    return youtube

def get_youtube_playlists(youtube_api_client):
    request = youtube_api_client.playlists().list(
        part="snippet",
        maxResults=50,
        mine=True
    )
    response = request.execute()

    playlists = response.get('items', [])

    return playlists

def delete_youtube_playlist(youtube_api_client, playlist_id):
    request = youtube_api_client.playlists().delete(id=playlist_id)
    request.execute()

def create_youtube_playlist(youtube_api_client, playlist_name):
    """
    Creates a new YouTube playlist with the given name using the YouTube API client.

    Args:
        playlist_name (str): The name of the playlist to be created.
        youtube_api_client: The YouTube API client object.


    Returns:
        str: The ID of the created playlist.
        str: The URL to the created playlist.

    Raises:
        HttpError: If an HTTP error occurs during the playlist creation.
    """
    existing_playlists = get_youtube_playlists(youtube_api_client)
    # Check if a playlist with the same name already exists
    # Delete it if thats the case
    if existing_playlists:
        for playlist in existing_playlists:
            if playlist['snippet']['title'] == playlist_name:
                print(f"A playlist with the name '{playlist_name}' already exists. Deleting it...")
                delete_youtube_playlist(youtube_api_client, playlist['id'])
                break
        
    new_playlist = {
        "snippet": {
            "title": playlist_name
        },
        "status": {
            "privacyStatus": "public"
        }
    }
    # Insert the playlist
    try:
        response = youtube_api_client.playlists().insert(
            part="snippet,status",
            body=new_playlist
        ).execute()
    except HttpError as e:
        print(f"An HTTP error {e.resp.status} occurred:\n{e.content}")
        return None
    # Return the ID of the created playlist
    return response["id"]

def create_youtube_query(track, tracklist):
    artist_string = ' '.join(tracklist[track])
    youtube_query = track + ' ' + artist_string # + ' lyrics'
    return youtube_query

def search_youtube_video(query):
    """
    Searches for a YouTube video by keywords and returns the first result.

    Args:
        query (str): The search keywords.

    Returns:
        str: The URL of the search result.
    """
    base_search_url = "https://www.googleapis.com/youtube/v3/search"
    # Parameters for the search request
    params = {
        "part": "snippet",
        "maxResults": 1,
        "q": query,
        "key": os.getenv('YT_API_KEY'),
        "type": "video"
    }
    response = requests.get(base_search_url, params=params)
    # Check if the request was successful
    if response.status_code == 200:
        video_id = response.json()["items"][0]["id"]["videoId"]
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        return video_url
    else:
        print(f"Search request failed with status code {response.status_code}")
        return None

def add_video_to_playlist(youtube_api_client, playlist_id, video_id):
    request = youtube_api_client.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                }
            }
        }
    )
    response = request.execute()
    return response


#%% Main   
def main():
    playlist_link = 'https://open.spotify.com/playlist/0G2Fto1sUommXvdFADH2yl?si=5399d29fc49747a0'
    #Authentifications
    spotify = authenticate_spotify()
    youtube_api_client = build_youtube_api_client()
    
    playlist_name, tracklist = get_spotify_playlist_info(spotify, playlist_link)
    # print(f'Playlist: {playlist_name}, Tracks: {tracklist}')
    # print(f'Playlist: {playlist_name}, Tracks: {tracklist}')
    
    try:
        playlist_id = create_youtube_playlist(youtube_api_client, playlist_name)
    except HttpError as e:
            if e.resp.status == 403:
                print("Quota exceeded. Operation aborted.")
                sys.exit(1)
            else:
                print(f"HttpError occurred: {e}")
                sys.exit(1)
        
    for track in tracklist:
        try:
            query = create_youtube_query(track, tracklist)
            # print(query)
            url = search_youtube_video(query)
            # print(url)
            
            video_id = url.split("v=")[1]
            add_video_to_playlist(youtube_api_client, playlist_id, video_id)
        except AttributeError:
            print(query)
            continue
        except HttpError as e:
            if e.resp.status == 403:
                print("Quota exceeded. Operation aborted.")
                sys.exit(1)
            else:
                print(f"HttpError occurred: {e}")
                continue
        

    print('All done!')
    youtube_playlist_link = f"https://www.youtube.com/playlist?list={playlist_id}"
    print(f'Here is the link to your playlist:\n{youtube_playlist_link}')

    

if __name__ == "__main__":
    main()
