from typing import List

from pyyoutube import Api as ytApi
from youtube_search import YoutubeSearch
from youtube_transcript_api import YouTubeTranscriptApi as tsApi


class Scraper:

    def __init__(self, gd3api_key):
        self.yt = ytApi(api_key=gd3api_key)

    def scrape(self, playlist: str) -> str:
        """Returns concatenated transcript text."""
        videos = self.get_playlist_item_ids(playlist)
        return " ".join(list(map(self.get_transcript, videos)))

    def get_playlist_item_ids(self, playlist: str) -> List[str]:
        """Return list of video IDs for items in playlist."""
        resp = self.yt.get_playlist_items(playlist_id=playlist, count=None)
        return [_i.snippet.resourceId.videoId for _i in resp.items]

    def get_transcript(self, video: str) -> str:
        """Returns"""
        resp = tsApi.get_transcript(video_id=video)
        parts = [_i["text"] for _i in resp]
        return " ".join(parts)

    def video_has_en_ts(self, video: str) -> bool:
        res = tsApi.list_transcripts(video)
        return True if res.find_generated_transcript(["en"]) else False


    # Finding and parsing playlist metadata

    def find_playlists(self, game: str) -> dict:
        res = self.yt.search_by_keywords(q=f"{game}", 
                                         search_type="playlist",
                                         count=999,
                                         return_json=True)
        return map(self.trim_metadata, res.items())

    def trim_metadata(self, playlist_json: dict) -> dict:
        return {"playlist_id": playlist_json["id"]["playlistId"],
                "playlist_title": playlist_json["snippet"]["title"],
                "channel_id": playlist_json["snippet"]["channelId"],
                "channel_name": playlist_json["channelTitle"]
                }