import reddit_api
import database
from typing import List


class CommentNode:
    """Holds Reddit comments in a two-way tree structure"""

    comment: reddit_api.RedditComment
    parent: None  # TODO
    children: None  # TODO

    def __init__(self, comment: reddit_api.RedditComment) -> None:
        self.comment = comment
        self.parent = None
        self.children = []

    def build_partial_comment_tree(self, db: database.SQLiteManager) -> None:  # TODO
        """Constructs a tree of comments top-down with this CommentNode being the root of the tree"""
        cur = db.conn.cursor()
        for child_id in cur.execute(
            "SELECT COMMENT_ID FROM comments WHERE PARENT_ID=?", self.comment.comment_id
        ):
            comment = reddit_api.RedditComment.from_db(child_id, db)
            node = CommentNode(comment)
            node.parent = self
            node.build_partial_comment_tree(db)
            self.children.append(node)

        cur.close()
        return self

    def build_full_comment_tree(self, db: database.SQLiteManager) -> None:  # TODO
        """Attempts to locate the top-level parent of this CommentNode before constructing a full tree top-down"""
        top = self
        while top.comment.parent_id[:2] != "t3":
            top = reddit_api.RedditComment.from_db(top.comment.parent_id, db)

        return top.build_partial_comment_tree(db)
