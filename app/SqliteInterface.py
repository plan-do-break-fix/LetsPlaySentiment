import sqlite3
from typing import List


# id exclusively refers to YouTube alphanumeric id
# pks are all referenced with rowid
TABLES = {
    "playlists": (
        "CREATE TABLE IF NOT EXISTS 'playlists' ("
        "  id TEXT NOT NULL,"
        "  title TEXT NOT NULL,"
        "  channel INTEGER NOT NULL,"
        "  game INTEGER NOT NULL,"
        "  transcribed INTEGER NOT NULL,"
        "  retrieved INTEGER DEFAULT 0,"
        "  FOREIGN KEY (channel) REFERENCES channel (rowid),"
        "  FOREIGN KEY (game) REFERENCES games (rowid)"
        ");"
    ),
    "channels": (
        "CREATE TABLE IF NOT EXISTS 'channels' ("
        "  name TEXT NOT NULL,"
        "  id TEXT NOT NULL"
        ");"
    ),
    "games": (
        "CREATE TABLE IF NOT EXISTS 'games' ("
        "  name TEXT NOT NULL,"
        "  searched INTEGER DEFAULT 0"
        ");"
    )
}


class SqliteInterface:

    def __init__(self):
        self.conn = sqlite3.connect("/data/transcripts.sqlite3.db")
        self.c = self.conn.cursor()
        for table in TABLES:
            self.c.execute(TABLES[table])
        self.conn.commit()
    
    def get_unprocessed(self) -> List[str]:
        self.c.execute("SELECT id FROM playlists WHERE "\
                       "transcribed=1 AND retrieved=0;")
        return self.c.fetchall()

    def get_transcribed_unknown(self) -> List[str]:
        self.c.execute("SELECT id FOM playlists WHERE "\
                       "transcribed=NULL")
        return self.c.fetchall()

    def get_unsearched(self) -> int:
        self.c.execute("SELECT name FROM games WHERE searched=0")
        return self.c.fetchall()

    def mark_as_retrieved(self, playlist: str) -> bool:
        self.c.execute("UPDATE playlists SET retrieved=1 WHERE id=?",
                       (playlist,))
        self.conn.commit()
        return True

    def mark_as_transcribed(self, playlist: str, value: int) -> bool:
        if value not in [0,1]:
            raise ValueError
        self.c.execute("UPDATE playlists SET transcribed=? WHERE id=?",
                       (value, playlist))
        self.conn.commit()
        return True

    def mark_as_searched(self, game: str) -> bool:
        self.c.execute("UPDATE games SET searched=1 WHERE name=?",
                       (game,))
        self.conn.commit()
        return True

    def get_channel_pk(self, channel: str) -> int:
        self.c.execute("SELECT rowid FROM channels WHERE id=?",
                       (channel,))
        return self.c.fetchone()[0]

    def get_game_pk(self, game: str) -> int:
        self.c.execute("SELECT rowid FROM games WHERE name=?", (game,))
        return self.c.fetchone()[0]

    # Existence Checks

    def channel_exists(self, channel: str) -> bool:
        self.c.execute("SELECT rowid FROM channels WHERE name=?",
                      (channel,))
        return True if self.c.fetchone() else False

    def game_exists(self, game: str) -> bool:
        self.c.execute("SELECT rowid FROM games WHERE name=?", (game,))
        return True if self.c.fetchone() else False

    def playlist_exists(self, playlist: str) -> bool:
        self.c.execute("SELECT rowid FROM playlists WHERE id=?",
                       (playlist,))
        return True if self.c.fetchone() else False

    # Insertion Methods

    def new_channel(self, name: str, id: str) -> int:
        self.c.execute("INSERT INTO channels (name, id) VALUES (?,?)", 
                       (name, id))
        self.conn.commit()
        return self.c.lastrowid

    def new_playlist(self, id: str, title:str, channel_pk: int, 
                     game_pk: int, transcribed: int) -> int:
        self.c.execute("INSERT INTO playlists "\
                       "(id, title, channel, game, transcribed) "\
                       "VALUES (?,?,?,?,?)",
                       (id, title, channel_pk, game_pk, transcribed))
        self.conn.commit()
        return self.c.lastrowid
