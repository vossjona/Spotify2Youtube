# Spotify2Youtube
Converts a Spotify Playlist to a Youtube Playlist.
Useful for Discord Music Bots that don't have access to Spotify.

## Prerequisites:
Developed on Python 3.11, should work for python 3.5 or newer
External Libraries:
- [Spotipy](https://spotipy.readthedocs.io/en/2.22.1/#) - Python library for the Spotify Web API
- [Google API Client](https://developers.google.com/youtube/v3/quickstart/python?hl=de)

- [Spotify Web Client API Key](https://developer.spotify.com/documentation/web-api) and Client Secret; should be stored as environment variables for Spotipy to work with them.
- Youtube API Key, also stored as an environment variable in this version.
- OAuth 2.0-Client-ID and Secret; best stored in a JSON file in your working directory.

## How to run:
1. Install libraries
2. Get and store keys at correct places
3. Insert link to spotify playlist in main()
4. Be sure your Gmail Account is also a YouTube channel and you can create playlists
5. Run
6. Login to YT Account
7. Refresh YT Account page
