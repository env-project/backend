from enum import Enum


class IsAuthor(str, Enum):
    ME = "me"


class IsBookmarked(str, Enum):
    ME = "me"


class SortBy(str, Enum):
    LATEST = "latest"
    COMMENTS = "comments"
    VIEWS = "views"
    BOOKMARK = "bookmark"