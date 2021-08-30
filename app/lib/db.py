import os
import sqlite3


class DB:
    def __init__(self):
        self.con = sqlite3.connect(os.getenv('DATABASE'))
        self.con.row_factory = sqlite3.Row

    def query(self, query: str, _commit: bool = True, **replacers):
        """
        Executes a given query against the database

        `replacers` are slurped from the kwargs and only support ':named' placeholders.

        The `_commit` flag can be set to False to disable committing the transaction
        """
        cursor = self.con.cursor()
        cursor.execute(query, dict(replacers))

        if _commit:
            self.con.commit()

        return cursor

    def __del__(self):
        self.con.close()
