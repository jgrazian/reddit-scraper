# Main script to scrape reddit comments

from reddit_api import *
from database import SQLiteManager


# Create or open a database
db = SQLiteManager("./data/main.db")

subreddit = input("Enter subreddit to scrape: ")

api = RedditApi()
delay = 10.0
delay_inc = 1.0
monitor = api.monitor_comments(subreddit, 10.0)

comments = []
while True:
    if not comments:
        comments = next(monitor)
    else:
        comments = monitor.send(delay)

    num_failed = 0
    for comment in comments:
        res = db.query_insert_comment(comment)
        if not res:
            num_failed += 1

    # We want some overlap to make sure not missing any new comments
    # But not too much overlap. So update the delay accordingly
    if num_failed > 8:
        delay += delay_inc
        delay_inc += delay_inc
    elif num_failed <= 1:
        delay *= 0.5
        delay_inc = 1.0

    if delay > 60.0:
        delay = 60.0
        delay_inc = 1.0

    print(
        f"Got {len(comments) - num_failed} new comments out of {len(comments)}. Next query delay {delay}s."
    )
