import os
from typing import List

from Matching import confirmed_match, load_search_terms


class App:

    def __init__(self):
        self.terms = self.load_search_terms()

    def collect_playlists(self, game_title: str) -> List[str]:
        """Return list of ids for confirmed matching transcribed playlists.""" 
        candidates = self.db.get_candidates(game_title)
        matching = [playlist for playlist in candidates \
                    if confirmed_match(self.db.get_playlist_title(playlist), 
                                       **self.terms[game_title])]
        return matching

    def load_transcript(playlist: str) -> str:
        """Returns text of transcripts from local storage."""
        if not os.path.isfile(f"/data/transcripts/{playlist}.txt"):
            return ""
        with open(f"/data/transcripts/{playlist}.txt", "r") as _f:
            return _f.read()

