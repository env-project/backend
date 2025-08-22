class UserNotFound(Exception):
    """
    사용자를 찾을 수 없을 때
    """

    def __init__(self, message: str = "해당 사용자를 찾을 수 없습니다."):
        self.message = message
        super().__init__(self.message)


class PostNotFound(Exception):
    """
    구인글을 찾을 수 없을 때
    """

    def __init__(self, message: str = "해당 구인글을 찾을 수 없습니다."):
        self.message = message
        super().__init__(self.message)


class CommentNotFound(Exception):
    """
    댓글을 찾을 수 없을 때
    """

    def __init__(self, message: str = "해당 댓글을 찾을 수 없습니다."):
        self.message = message
        super().__init__(self.message)


class NotFirstParentComment(Exception):
    """
    최상위 부모 댓글이 아닐 때
    """

    def __init__(self, message: str = "최상위 부모 댓글이 아닙니다."):
        self.message = message
        super().__init__(self.message)


class RecruitingCommentNotMatch(Exception):
    """
    구인글과 댓글이 일치하지 않을 때
    """

    def __init__(self, message: str = "해당 구인글에 대한 댓글이 아닙니다."):
        self.message = message
        super().__init__(self.message)


class UserNotRecruitingPostOwner(Exception):
    """
    구인글을 작성한 사용자가 아닐 때
    """

    def __init__(self, message: str = "해당 게시글에 대한 권한이 없습니다."):
        self.message = message
        super().__init__(self.message)


class UserNotCommentOwner(Exception):
    """
    댓글을 작성한 사용자가 아닐 때
    """

    def __init__(self, message: str = "해당 댓글에 대한 권한이 없습니다."):
        self.message = message
        super().__init__(self.message)


### 북마크
# 이미 북마크가 되어있을 때
class PostAlreadyBookmarked(Exception):
    def __init__(self, message: str = "이미 북마크된 구인글입니다."):
        self.message = message
        super().__init__(self.message)


class PostBookmarkNotFound(Exception):
    def __init__(self, message: str = "구인글 북마크를 찾을 수 없습니다."):
        self.message = message
        super().__init__(self.message)


class UserAlreadyBookmarked(Exception):
    def __init__(self, message: str = "이미 북마크된 회원입니다."):
        self.message = message
        super().__init__(self.message)


class UserBookmarkNotFound(Exception):
    def __init__(self, message: str = "사용자 북마크를 찾을 수 없습니다."):
        self.message = message
        super().__init__(self.message)
