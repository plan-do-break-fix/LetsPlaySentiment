from time import sleep
from typing import List
import youtube_transcript_api

from youtubesearchpython import Playlist, PlaylistsSearch
from youtube_transcript_api import YouTubeTranscriptApi as tsApi


class Scraper:

    def __init__(self):
        pass

    def scrape(self, playlist: str) -> str:
        """Returns concatenated transcript text."""
        videos = self.get_playlist_item_ids(playlist)
        return " ".join(list(map(self.get_transcript, videos)))

    def get_playlist_item_ids(self, playlist: str) -> List[str]:
        """Return list of video IDs for items in playlist."""
        videos = Playlist.getVideos(f"https://www.youtube.com/playlist?list={playlist}")["videos"]
        return [video["id"] for video in videos]

    def get_transcript(self, video: str) -> str:
        """Returns"""
        resp = tsApi.get_transcript(video_id=video)
        parts = [_i["text"] for _i in resp]
        return " ".join(parts)

    def video_has_en_ts(self, video: str) -> bool:
        try:
            res = tsApi.list_transcripts(video)
        except youtube_transcript_api._errors.TranscriptsDisabled:
            return False
        try:
            return True if res.find_generated_transcript(["en"]) else False
        except youtube_transcript_api._errors.NoTranscriptFound:
            return False


    # Finding and parsing playlist metadata

    def find_playlists(self, terms: str, attempt=0) -> List[dict]:
        search = PlaylistsSearch(terms)
        playlists = []
        try:
            while search.result()["result"] and len(playlists) < 980:
                playlists += search.result()["result"]
                search.next()
                sleep(5)  # HTTP requests need to be rate limited
            return [i for i in list(map(self.trim_metadata, playlists)) if i]
        except TypeError as err:
            if attempt < 5:
                return self.find_playlists(terms, attempt=attempt+1)
            else:
                print("Max retries reached on search.next() returns None.")
                return err

    def trim_metadata(self, playlist_json: dict) -> dict:
        return {"playlist_id": playlist_json["id"],
                "playlist_title": playlist_json["title"],
                "channel_id": playlist_json["channel"]["id"],
                "channel_name": playlist_json["channel"]["name"]
                }