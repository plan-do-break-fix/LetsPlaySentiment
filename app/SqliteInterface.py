import sqlite3
from typing import List


TABLES = {
    "playlists": (
        "CREATE TABLE IF NOT EXISTS 'playlists' ("
        "  id TEXT NOT NULL,"
        "  retrieved INTEGER DEFAULT 0,"
        "  channel INTEGER NOT NULL,"
        "  game INTEGER NOT NULL,"
        "  FOREIGN KEY (channel) REFERENCES channel (rowid),"
        "  FOREIGN KEY (game) REFERENCES games (rowid)"
        ");"
    ),
    "channels": (
        "CREATE TABLE IF NOT EXISTS 'channels' ("
        "  name TEXT NOT NULL,"
        "  url TEXT NOT NULL"
        ");"
    ),
    "games": (
        "CREATE TABLE IF NOT EXISTS 'games' ("
        "  name TEXT NOT NULL"
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
        self.c.execute("SELECT id FROM playlists WHERE retrieved=0;")
        return self.c.fetchall()

    def mark_as_retrieved(self, playlist: str) -> bool:
        self.c.execute("UPDATE playlists SET retrieved=1 WHERE id=?", (playlist,))
        self.conn.commit()
        return True

    def get_channel_pk(self, channel: str) -> int:
        self.c.execute("SELECT rowid FROM channels WHERE name=?", (channel,))
        return self.c.fetchone()[0]

    def get_game_pk(self, game: str) -> int:
        self.c.execute("SELECT rowid FROM games WHERE name=?", (game,))
        return self.c.fetchone()[0]

    


    