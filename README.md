# Reddit Scraper
A few simple scripts to collect reddit comments and attempt to determine a user's ability to drive engagement (and thus advertising value).

## Notes
Reddit comments are retrieved via https by simply doing a GET to `https://www.reddit.com/r/SUBREDDIT/comments.json`. The comments are then stored in a SQLite databse on disk for easy managment. 

Analysis will be done on top-level comments (comments directly on thread posts) and will attempt to score the amount of engagement a user can bring by doing a weighted count of the number of replies that user recieves (deeper comments being less impactful).

## Setting Up
1. Have python 3.8+ installed
2. Clone this repo 
`git clone https://github.com/jgrazian/reddit-scraper.git`
`> cd reddit-scraper`
2. Install deps `pip install -r requirements.txt`
3. Scrape comments `python scrape.py`
4. (NOT DONE) Run analysis `python main.py`

---
You can directly inspect the sqlite databse with a simple script like this
``` python
import sqlite3
conn = sqlite3.connect('./data/main.db')
cur = conn.cursor()

for comment in cur.execute('select * from comments'):
	print(comment)

cur.execute('select body from comments')
print(cur.fetchone())
```