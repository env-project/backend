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
