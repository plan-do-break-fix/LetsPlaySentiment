import re, string, os
from typing import List


from Matching import confirmed_match, load_search_terms
import Text as txt
import Tokens as tkn


class App:

    def __init__(self):
        self.terms = load_search_terms("search-terms.json")

    def collect_playlists(self, game_title: str) -> List[str]:
        """Return list of ids for confirmed matching transcribed playlists.""" 
        candidates = self.db.get_candidates(game_title)
        matching = [playlist for playlist in candidates \
                    if confirmed_match(self.db.get_playlist_title(playlist), 
                                       **self.terms[game_title])]
        return matching

    def load_transcript(self, playlist: str) -> str:
        """Returns text of transcripts from local storage."""
        if not os.path.isfile(f"/data/transcripts/{playlist}.txt"):
            return ""
        with open(f"/data/transcripts/{playlist}.txt", "r") as _f:
            return _f.read()


    def preprocess(self, text: str) -> List[str]:
        text = txt.expand_contractions(
               txt.strip_additions(
               txt.resurrect_expletives(text)))
        lemmas = tkn.lemmatize(
                 tkn.drop_stopwords(
                 tkn.tokenize(text)))
        return lemmas
