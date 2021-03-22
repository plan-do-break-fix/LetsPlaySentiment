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
        to_process = self.db.get_unprocessed()
        if not to_process:
            self.log.debug("Nothing to do. Waiting...")
            sleep(60)
            return None
        for playlist in to_process:
            self.log.debug(f"Processing playlist {playlist[0]}.")
            if self.process(playlist[0]):
                self.log.debug(f"Successfully processed {playlist[0]}.")

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