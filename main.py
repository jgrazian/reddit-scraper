# Main analysis file
import matplotlib.pyplot as plt

from comment_tree import CommentNode
from database import SQLiteManager
from reddit_api import RedditComment

db = SQLiteManager("./data/main.db")

top_level_comment = db.query_get_top_level_comment()

# Score top level comments, put results into score table
while top_level_comment:
    tree = CommentNode(top_level_comment)
    tree.build_comment_tree(db)

    db.query_insert_score(tree.comment.comment_id, tree.score(), tree.size())

    top_level_comment = db.query_get_top_level_comment()

# Finished all top level comments
# Aggregate score by Author
db.query_insert_author_table()

# Plot Author Aggregate
n = []
avg = []
for author in db.query_get_author_data():
    n.append(author[1])
    avg.append(author[3])

fig, ax = plt.subplots()
scatter = ax.scatter(n, avg)
ax.set_ylabel('Author Average Score')
ax.set_xlabel('Number of Comments')
plt.plot()

# Plot comment Pareto Front
n = []
score = []
for x in db.query_get_score_data():
    n.append(x[2])
    score.append(x[1])

fig, ax = plt.subplots()
scatter = ax.scatter(n, score)
ax.set_ylabel('Total Score')
ax.set_xlabel('Number of Comments in Tree')
plt.plot()
plt.show()