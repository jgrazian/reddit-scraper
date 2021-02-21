# Main analysis file
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
