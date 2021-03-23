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
        key = environ["GD3API_KEY"] if not envvars else envvars["GD3API_KEY"]
        self.scraper = Scraper(key)
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
        to_check = self.db.get_transcribed_unknown()
        # check if any new playlists have transcripts or not
        if to_check:
            for playlist in to_check:
                self.log.debug(f"Checking {playlist} for transcripts.")
                self.db.mark_as_transcribed(playlist, 
                                            int(self.check_is_transcribed(playlist)))
        # if previous entries are complete, find playlists for next game
        if not to_process and not to_check:
            to_search = self.db.get_unsearched()
            if not to_search:
                self.log.debug("Nothing to do. Waiting...")
                sleep(60)
                return None
            to_search = to_search.pop()
            playlist_dicts = self.scraper.find_playlists(f"play {to_search}")
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
                                         self.db.get_game_pk(to_search))
                    self.log.debug(f"Playlist for {to_search} by "\
                                    "{playlist['channel_name']} added.")
            self.db.mark_as_searched(playlist["playlist_id"])

    def check_is_transcribed(self, playlist: str) -> bool:
        return all(map(self.scraper.video_has_en_ts, 
                       self.scraper.get_playlist_item_ids(playlist)))


    def process(self, playlist: str) -> bool:
        ts = self.scraper.scrape(playlist)
        if not ts:
            self.log.error("Unable to retrieve transcript.")
            return False
        fpath = f"/data/transcripts/{playlist}.txt" 
        with open(fpath, "w") as _file:
            _file.write(ts)
        self.log.debug(f"Transcript file written to disk.")
        self.db.mark_as_retrieved(playlist)
        self.log.debug(f"Transcript marked as retrieved.")


if __name__ == "__main__":
    app = App()
    while True:
        app.cycle()