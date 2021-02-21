from __future__ import annotations
import json
from math import exp

from reddit_api import RedditComment
from database import SQLiteManager
from typing import List


class CommentNode:
    """Holds Reddit comments in a two-way tree structure"""

    comment: RedditComment
    parent: CommentNode | None
    children: List[CommentNode]

    def __init__(
        self, comment: RedditComment, parent: CommentNode | None = None
    ) -> None:
        self.comment = comment
        self.parent = None
        self.children = []

    def build_comment_tree(self, db: SQLiteManager) -> CommentNode:
        """Constructs a tree of comments top-down with this CommentNode being the root of the tree"""

        children = db.query_get_comments_by_parent_id(self.comment.comment_id)
        for child in children:
            node = CommentNode(child, self)
            node.build_comment_tree(db)
            self.children.append(node)

        return self

    def size(self) -> int:
        """Returns the total number of nodes in the tree"""
        size = 1
        for child in self.children:
            size += child.size()
        return size

    def score(self, depth: int = 0) -> float:
        """Generates an 'engagement score' with the equation score = 1/e^depth"""
        score = 1 / exp(depth)
        for child in self.children:
            score += child.score(depth + 1)
        if depth == 0:
            return score - 1
        else:
            return score

    def json(self) -> str:
        """Returns entire tree as JSON string"""

        def to_dict(node):
            l = {}
            for child in node.children:
                l[child.comment.comment_id] = to_dict(child)
            return l

        return json.dumps({self.comment.comment_id: to_dict(self)}, indent=2)
