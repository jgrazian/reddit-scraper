from __future__ import annotations

import sqlite3
import json
from typing import List

from reddit_api import RedditComment

TABLE_CONFIG = "./table_config.json"


class SQLiteManager:
    conn: sqlite3.Connection

    def __init__(self, database: str) -> None:
        try:
            self.conn = sqlite3.connect(database)

            cur = self.conn.cursor()
            cur.execute("PRAGMA strict=ON;")

            cur.execute(
                """ SELECT count(name) FROM sqlite_master WHERE type='table' AND name='comments' """
            )
            if cur.fetchone()[0] != 1:
                print(f"No tables found in database {database}. Creating tables...")
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
            cur.execute(f"DROP TABLE IF EXISTS {name}")
            MAKE_SQL = f"CREATE TABLE {name} ("
            for column in table["columns"]:
                MAKE_SQL += f"{column}, "

            MAKE_SQL = MAKE_SQL[:-2] + ");"  # Remove trailing comma
            cur.execute(MAKE_SQL)

        self.conn.commit()
        cur.close()

    def query_insert_comment(self, comment: RedditComment) -> bool:
        cur = self.conn.cursor()

        try:
            cur.execute(
                "INSERT INTO comments VALUES (?,?,?,?,?,?,?);",
                (
                    comment.comment_id,
                    comment.created_utc,
                    comment.author,
                    comment.body,
                    comment.link_id,
                    comment.parent_id,
                    comment.subreddit_id,
                ),
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            # print(e)
            return False
        finally:
            self.conn.commit()
            cur.close()

    def query_get_comment_by_id(self, comment_id: str) -> RedditComment | None:
        cur = self.conn.cursor()

        try:
            cur.execute("SELECT * FROM comments WHERE COMMENT_ID=?", comment_id)
            res = cur.fetchone()

            return RedditComment(
                comment_id=res[0],
                created_utc=res[1],
                author=res[2],
                body=res[3],
                link_id=res[4],
                parent_id=res[5],
                subreddit_id=res[6],
            )
        except sqlite3.Error as e:
            print(e)
            return None
        finally:
            self.conn.commit()
            cur.close()

    def query_get_comments_by_parent(self, parent_id: str) -> List[RedditComment]:
        cur = self.conn.cursor()

        try:
            cur.execute("SELECT * FROM comments WHERE PARENT_ID=?", parent_id)
            res = cur.fetchone()

            comments = []
            for r in res:
                comment = RedditComment(
                    comment_id=r[0],
                    created_utc=r[1],
                    author=r[2],
                    body=r[3],
                    link_id=r[4],
                    parent_id=r[5],
                    subreddit_id=r[6],
                )
                comments.append(comment)

            return comments

        except sqlite3.Error as e:
            print(e)
            return []
        finally:
            self.conn.commit()
            cur.close()


if __name__ == "__main__":
    db = SQLiteManager("./test.db")