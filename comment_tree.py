from __future__ import annotations

from reddit_api import RedditComment
from database import SQLiteManager
from typing import List


class CommentNode:
    """Holds Reddit comments in a two-way tree structure"""

    comment: RedditComment
    parent: CommentNode | None
    children: List[CommentNode]

    def __init__(self, comment: RedditComment) -> None:
        self.comment = comment
        self.parent = None
        self.children = []

    def build_partial_comment_tree(self, db: SQLiteManager) -> CommentNode:
        """Constructs a tree of comments top-down with this CommentNode being the root of the tree"""

        for child in db.query_get_comments_by_parent(self.comment.comment_id):
            node = CommentNode(child)
            node.parent = self
            node.build_partial_comment_tree(db)
            self.children.append(node)

        return self

    def build_full_comment_tree(self, db: SQLiteManager) -> CommentNode:
        """Attempts to locate the top-level parent of this CommentNode before constructing a full tree top-down"""
        top = self.comment
        while top.parent_id[:2] != "t3":
            top = db.query_get_comment_by_id(top.parent_id)

        return CommentNode(top).build_partial_comment_tree(db)
