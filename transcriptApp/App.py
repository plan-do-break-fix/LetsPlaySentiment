import logging
from os import environ
from time import sleep

from Scraper import Scraper
from SqliteInterface import SqliteInterface

class App:

    def __init__(self, envvars={}):
        self.setup_logging()
        self.log.debug("Initializing application..."
                      ) if not envvars else self.log.debug(
                      "Initializing with dummy variables...")
        self.scraper = Scraper()
        self.log.debug("Scraper successfully initialized.")
        self.db = SqliteInterface()
        self.log.debug("Database interface successfully initialized.")

    def setup_logging(self):
        self.log = logging.getLogger("Transcipts")
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
                    "%(asctime)s [%(name)s] %(levelname)-8s %(message)s")
        handler.setFormatter(formatter)
        self.log.addHandler(handler)
        self.log.setLevel(logging.DEBUG)

    def cycle(self) -> None:
        # download transcripts waiting for download
        to_process = self.db.get_unprocessed()
        if to_process:
            for playlist in to_process:
                self.log.debug(f"Processing playlist {playlist[0]}.")
                if self.process(playlist[0]):
                    self.log.debug(f"Successfully processed {playlist[0]}.")
                else:
                    self.db.mark_as_transcribed(playlist[0], 0)
                    self.log.error(f"Failure processing {playlist[0]}.")
        # if previous entries are complete, find playlists for next game
        if not to_process:
            to_search = self.db.get_unsearched()
            if not to_search:
                self.log.debug("Nothing to do. Waiting...")
                sleep(60)
                return None
            to_search = to_search.pop()[0]
            self.log.debug(f"Attempting to retrieve playlists for {to_search}.")
            playlist_dicts = self.scraper.find_playlists(f"lets play {to_search}")
            self.log.debug(f"Found {len(playlist_dicts)} playlists for {to_search}.")
            for playlist in playlist_dicts:
                if not self.db.playlist_exists(playlist["playlist_id"]):
                    self.log.debug("New playlist encountered.")
                    if not self.db.channel_exists(playlist["channel_id"]):
                        self.db.new_channel(playlist["channel_name"], 
                                            playlist["channel_id"])
                        self.log.debug(f"Channel {playlist['channel_name']} added.")
                    self.db.new_playlist(playlist["playlist_id"],
                                         playlist["playlist_title"],
                                         self.db.get_channel_pk(playlist["channel_id"]),
                                         self.db.get_game_pk(to_search),
                                         int(self.check_is_transcribed(playlist["playlist_id"])))
                    self.log.debug(f"Playlist for {to_search} by "\
                                   f"{playlist['channel_name']} added.")
            self.db.mark_as_searched(to_search)

    def check_is_transcribed(self, playlist: str) -> bool:
        try:
            return all(map(self.scraper.video_has_en_ts, 
                       self.scraper.get_playlist_item_ids(playlist)))
        except TypeError:
            return False


    def process(self, playlist: str) -> bool:
        ts = self.scraper.scrape(playlist)
        if not ts:
            return False
        fpath = f"/data/transcripts/{playlist}.txt" 
        with open(fpath, "w") as _file:
            _file.write(ts)
        self.log.debug(f"Transcript file written to disk.")
        self.db.mark_as_retrieved(playlist)
        self.log.debug(f"Transcript marked as retrieved.")
        return True


if __name__ == "__main__":
    app = App()
    while True:
        app.cycle()