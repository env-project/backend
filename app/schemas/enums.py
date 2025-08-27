from enum import Enum


class IsBookmarked(str, Enum):
    ME = "me"


class SortBy(str, Enum):
    LATEST = "latest"
    COMMENTS = "comments"
    VIEWS = "views"
    BOOKMARK = "bookmark"
