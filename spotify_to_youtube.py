import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

# Enter your Spotify API credentials
SPOTIPY_CLIENT_ID = "SPOTIPY_CLIENT_ID"
SPOTIPY_CLIENT_SECRET = "SPOTIPY_CLIENT_SECRET"
SPOTIPY_REDIRECT_URI = "http://localhost:8888/callback"

# Enter your YouTube API credentials
CLIENT_SECRETS_FILE = "directorypath/client_secret.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

def get_spotify_playlist_tracks(username, playlist_id):
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                                   client_secret=SPOTIPY_CLIENT_SECRET,
                                                   redirect_uri=SPOTIPY_REDIRECT_URI,
                                                   scope="playlist-read-private"))
    results = sp.user_playlist_tracks(username, playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks

def create_youtube_playlist(youtube, title, description):
    request = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": ["Spotify", "Music"],
                "defaultLanguage": "en"
            },
            "status": {
                "privacyStatus": "private"
            }
        }
    )
    response = request.execute()
    return response["id"]

def add_video_to_youtube_playlist(youtube, playlist_id, video_id):
    request = youtube.playlistItems().insert(
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
    request.execute()

def search_youtube_video(youtube, query):
    request = youtube.search().list(
        part="snippet",
        q=query,
        maxResults=1,
        type="video"
    )
    response = request.execute()
    return response["items"][0]["id"]["videoId"] if response["items"] else None

def main():
    username = 'your_username'
    playlist_id = 'your_playlist_id'

    tracks = get_spotify_playlist_tracks(username, playlist_id)

    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_local_server(port=0)
    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

    playlist_title = "My Spotify Playlist on YouTube"
    playlist_description = "A playlist created from my Spotify playlist."
    youtube_playlist_id = create_youtube_playlist(youtube, playlist_title, playlist_description)

    for track in tracks:
        song_name = track['track']['name']
        artist_name = track['track']['artists'][0]['name']
        search_query = f"{song_name} {artist_name}"
        video_id = search_youtube_video(youtube, search_query)
        if video_id:
            add_video_to_youtube_playlist(youtube, youtube_playlist_id, video_id)
            print(f"Added {song_name} by {artist_name} to the YouTube playlist")

if __name__ == "__main__":
    main()
