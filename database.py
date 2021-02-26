from __future__ import annotations

import sqlite3
import json
from typing import List, Any, Iterable

from reddit_api import RedditComment

TABLE_CONFIG = "./table_config.json"


class SQLiteManager:
    conn: sqlite3.Connection

    def __init__(self, database: str) -> None:
        try:
            self.conn = sqlite3.connect(database)

            cur = self.conn.cursor()
            cur.execute("PRAGMA strict=ON;")

            self._create_tables()

            self.conn.commit()
            cur.close()

            print(f"Opened SQLite connection to {database}")
        except sqlite3.Error as e:
            print(e)

    def _create_tables(self) -> None:
        cur = self.conn.cursor()

        # Reads tables from TABLE_CONFIG file
        table_config = json.load(open(TABLE_CONFIG, "r"))
        for table in table_config["tables"]:
            name = table["name"]
            print(f"Creating table {name}...")
            MAKE_SQL = f"CREATE TABLE IF NOT EXISTS {name} ("
            for column in table["columns"]:
                MAKE_SQL += f"{column}, "

            MAKE_SQL = MAKE_SQL[:-2] + ");"  # Remove trailing comma
            cur.execute(MAKE_SQL)

        self.conn.commit()
        cur.close()

    def _insert(self, query: str, values: Iterable[Any] = ()) -> bool:
        cur = self.conn.cursor()

        try:
            cur.execute(query, values)
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            return False
        finally:
            cur.close()

    def _select(self, query: str, values: Iterable[Any] = ()) -> List[Any]:
        cur = self.conn.cursor()

        try:
            cur.execute(query, values)
            return cur.fetchall()
        except sqlite3.Error as e:
            return []
        finally:
            cur.close()

    def query_insert_comment(self, comment: RedditComment) -> bool:
        """Inserts a RedditComment into the comments table"""
        query = "INSERT INTO comments VALUES (?,?,?,?,?,?,?);"
        values = (
            comment.comment_id,
            comment.created_utc,
            comment.author,
            comment.body,
            comment.link_id,
            comment.parent_id,
            comment.subreddit_id,
        )
        return self._insert(query, values)

    def query_insert_score(self, id: str, score: float, size: int) -> bool:
        """Inserts a comment_id and score into the score table"""
        query = "INSERT INTO score VALUES (?,?,?);"
        values = (id, score, size)
        return self._insert(query, values)

    def query_insert_author_table(self) -> bool:
        """Aggregate all of an author's comments into a total score"""
        query = """INSERT OR REPLACE INTO author SELECT
                        a.AUTHOR,
                        COUNT(b.SCORE) "COMMENT_COUNT",
                        SUM(b.SCORE) "TOTAL_SCORE",
                        SUM(b.SCORE) / COUNT(b.SCORE) "AVERAGE_SCORE"
                    FROM
                        comments a,
                        score b
                    WHERE
                        a.COMMENT_ID = b.COMMENT_ID
                    GROUP BY
                        a.AUTHOR
                """

        return self._insert(query)

    def query_get_comment_by_id(self, comment_id: str) -> RedditComment | None:
        query = "SELECT * FROM comments WHERE COMMENT_ID=?"
        values = [comment_id]

        res = self._select(query, values)

        if res:
            return RedditComment(*res[0])
        else:
            return None

    def query_get_comments_by_parent_id(self, parent_id: str) -> List[RedditComment]:
        """Gets all child comments given a parent's comment_id"""
        query = "SELECT * FROM comments WHERE PARENT_ID=?"
        values = [parent_id]

        comments = []
        for r in self._select(query, values):
            comments.append(RedditComment(*r))

        return comments

    def query_get_top_level_comment(self) -> RedditComment | None:
        """Selects a random comment who's parent is a reddit post (t3_ type)"""
        query = """SELECT * FROM comments 
                            WHERE PARENT_ID LIKE "t3_%" 
                            AND COMMENT_ID NOT IN (SELECT COMMENT_ID FROM score) ORDER BY RANDOM() LIMIT 1"""

        res = self._select(query)

        if res:
            return RedditComment(*res[0])
        else:
            return None

    def query_get_author_data(self):
        query = """SELECT * FROM author
                        ORDER BY AVERAGE_SCORE"""
        return self._select(query)
    
    def query_get_score_data(self):
        query = """SELECT * FROM score"""
        return self._select(query)


if __name__ == "__main__":
    db = SQLiteManager("./data/main.db")

    print(db.query_get_top_level_comment())
