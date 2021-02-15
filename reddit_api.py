import requests
import time
from typing import List
from dataclasses import dataclass

from database import SQLiteManager


@dataclass
class RedditComment:
    """
    A basic reddit comment.

    This class excludes much of the data that comes with
    a reddit comment in favor of simplicity.
    """

    comment_id: str = ""
    created_utc: float = 0
    author: str = ""
    body: str = ""
    link_id: str = ""
    parent_id: str = ""
    subreddit_id: str = ""

    def to_db(self, db: SQLiteManager) -> None:
        cur = db.conn.cursor()

        try:
            cur.execute(
                "INSERT INTO comments VALUES (?,?,?,?,?,?,?);",
                (
                    self.comment_id,
                    self.created_utc,
                    self.author,
                    self.body,
                    self.link_id,
                    self.parent_id,
                    self.subreddit_id,
                ),
            )
        except:
            print("Failed to insert comment")
        finally:
            cur.close()

    def from_db(comment_id: str, db: SQLiteManager) -> None:  # TODO
        cur = db.conn.cursor()

        try:
            res = cur.fetchone("SELECT * FROM comments WHERE COMMENT_ID=?", comment_id)

            return RedditComment(
                comment_id=res[0],
                created_utc=res[1],
                author=res[2],
                body=res[3],
                link_id=res[4],
                parent_id=res[5],
                subreddit_id=res[6],
            )
        except:
            print("Failed to retrieve comment")
        finally:
            cur.close()


class RedditApi:
    """A class to get data from Reddit."""

    def get_latest_comments(self, subreddit: str) -> List[RedditComment]:
        r = requests.get(
            f"https://reddit.com/r/{subreddit}/comments.json",
            headers={"User-agent": "TestBot v0.1"},
        )

        comments = []
        if r.status_code == 200:
            data = r.json()

            for child in data["data"]["children"]:
                child = child["data"]

                comment = RedditComment()
                comment.link_id = child["link_id"]
                comment.author = child["author"]
                comment.created_utc = child["created_utc"]
                comment.parent_id = child["parent_id"]
                comment.subreddit_id = child["subreddit_id"]
                comment.body = child["body"]
                comment.comment_id = child["name"]

                comments.append(comment)

        return comments

    def monitor_comments(self, subreddit: str, delay: int = 15) -> List[RedditComment]:
        next_time = 0

        while True:
            if time.time() > next_time:
                yield self.get_latest_comments(subreddit)
                next_time = time.time() + delay
            else:
                time.sleep(1.0)

    def get_link_comments(self, link_id: str) -> List[RedditComment]:
        # Get comments given reddit link_id
        pass


if __name__ == "__main__":
    api = RedditApi()

    for comments in api.monitor_comments("news", 10):
        for comment in comments:
            print(comment.body)
