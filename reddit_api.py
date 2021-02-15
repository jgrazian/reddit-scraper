from __future__ import annotations

import requests
import time
from typing import List, TypedDict, Generator
from dataclasses import dataclass


@dataclass
class RedditComment:
    """
    A basic reddit comment.

    This class excludes much of the data that comes with
    a reddit comment in favor of simplicity.
    """

    comment_id: str
    created_utc: int
    author: str
    body: str
    link_id: str
    parent_id: str
    subreddit_id: str


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

                comment = RedditComment(
                    comment_id=child["name"],
                    created_utc=child["created_utc"],
                    author=child["author"],
                    body=child["body"],
                    link_id=child["link_id"],
                    parent_id=child["parent_id"],
                    subreddit_id=child["subreddit_id"],
                )

                comments.append(comment)

        return comments

    def monitor_comments(
        self, subreddit: str, delay: float = 15.0
    ) -> Generator[List[RedditComment], float, RedditComment]:
        next_time = 0.0

        while True:
            if time.time() > next_time:
                new_delay = yield self.get_latest_comments(subreddit)
                if new_delay:
                    delay = new_delay
                next_time = time.time() + delay
            else:
                time.sleep(1.0)


if __name__ == "__main__":
    subreddit = input("Enter subreddit name to monitor: ")
    api = RedditApi()

    for comments in api.monitor_comments("news"):
        for comment in comments:
            print(comment.body)
