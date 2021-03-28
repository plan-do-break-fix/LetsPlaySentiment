import logging
from time import sleep

from Matching import confirmed_match, load_search_terms
from Scraper import Scraper
from SqliteInterface import SqliteInterface

class App:

    def __init__(self):
        self.setup_logging()
        self.game_terms = load_search_terms("search-terms.json")
        self.log.debug("Game terms loaded.")
        self.scraper = Scraper()
        self.log.debug("Scraper initialized.")
        self.db = SqliteInterface()
        self.log.debug("Database interface initialized.")
        self.update_games()

    def setup_logging(self):
        self.log = logging.getLogger("TransciptApp")
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
                    "%(asctime)s [%(name)s] %(levelname)-8s %(message)s")
        handler.setFormatter(formatter)
        self.log.addHandler(handler)
        self.log.setLevel(logging.DEBUG)

    def update_games(self) -> None:
        new_games = [g for g in self.game_terms.keys() 
                         if not self.db.game_exists(g)]
        for game in new_games:
            self.db.new_game(game)
        if new_games:
            self.log.info(f"{len(new_games)} games added to database.")

    def cycle(self) -> None:
        """Processing tasks to be performed for each game title."""
        to_search = self.db.get_unsearched()
        if not to_search:
            self.log.warning("Nothing to do. Waiting...")
            sleep(60)
        game_name = to_search.pop()[0]
        self.log.info(f"Finding playlists for {game_name}.")
        # Find new playlists for game
        playlist_dicts = self.scraper.find_playlists(f"lets play {game_name}")
        new_playlists = [p for p in playlist_dicts \
                         if not self.db.playlist_exists(p["playlist_id"])]
        for playlist in new_playlists:
            self.db.new_playlist(playlist["playlist_id"],
                                 playlist["playlist_title"])
        self.log.info(f"{len(new_playlists)} new playlists found.")
        # Find candidate playlists and associate with a channel
        candidates = []
        for p in new_playlists:
            if self.db.channel_exists(p["channel_id"]):
                self.db.associate_with_channel(p["playlist_id"],
                                        self.db.get_channel_pk(p["channel_id"]))
                candidates.append(p)
            else:
                self.db.associate_with_channel(p["channel_id"], 0)
        self.log.info(f"{len(candidates)} candidate playlists found.")
        # Find candidate playlists and associate with matching game 
        matches = []
        for c in candidates:
            matching_game = self.match_to_game(c["playlist_title"])
            if matching_game:
                if not self.db.game_exists(matching_game):
                    self.log.critical(f"Game terms key {matching_game} does not"
                                      " match any game title in database.")
                    raise RuntimeError
                self.db.associate_with_game(c["playlist_id"],
                                            self.db.get_game_pk(matching_game))
                c["game"] = self.db.get_game_pk(matching_game)
                matches.append(c)
            else:
                self.db.associate_with_game(c["playlist_id"], 0)
        self.log.info(f"{len(matches)} confirmed matches found.")
        # Find transcribed matches and fetch transcripts
        for m in matches:
            if self.is_transcribed(m["playlist_id"]):
                self.db.mark_as_transcribed(m["playlist_id"], 1)
                _title = m["playlist_title"] if \
                         len(m["playlist_title"]) < 36 \
                         else f"{m['playlist_title'][:35]}..."
                self.log.info(f"\"{_title}\" added to catalog.")
                if self.write_to_disk(m["playlist_id"]):
                    self.db.mark_as_retrieved(m["playlist_id"])
                    self.log.info(f"\"{_title}\" saved to disk.")
                else:
                    self.db.mark_as_retrieved(m["playlist_id"], value=0)
            else:
                self.db.mark_as_transcribed(m["playlist_id"], 0)
        self.db.mark_as_searched(game_name)

    def is_transcribed(self, playlist: str) -> bool:
        """Return True if all videos in playlist have English transcripts."""
        try:
            return all(map(self.scraper.video_has_en_ts, 
                       self.scraper.get_playlist_item_ids(playlist)))
        except TypeError:
            return False

    def write_to_disk(self, playlist: str) -> bool:
        ts = self.scraper.scrape(playlist)
        if not ts:
            return False
        fpath = f"/data/transcripts/{playlist}.txt" 
        with open(fpath, "w") as _file:
            _file.write(ts)
        return True

    def match_to_game(self, title: str) -> str:
        games = [g for g in self.game_terms.keys() \
                 if confirmed_match(title.lower(), **self.game_terms[g])]
        if len(games) > 1:
            sims_games = [g for g in games if "The Sims" in g]
            if sims_games and len(sims_games) == 1:
                return sims_games[0]
            self.log.critical("Search term integrity failure.")
            self.log.critical(f"{games} have matching terms in {title}.")
            raise RuntimeError
        return games[0] if games else ""

if __name__ == "__main__":
    app = App()
    while True:
        app.cycle()