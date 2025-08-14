class PostNotFound(Exception):
    """
    구인글을 찾을 수 없을 때
    """

    def __init__(self, message: str = "해당 구인글을 찾을 수 없습니다."):
        self.message = message
        super().__init__(self.message)

class BookmarkNotFound(Exception):
    """
    북마크를 찾을 수 없을 때
    """

    def __init__(self, message: str = "해당 북마크를 찾을 수 없습니다."):
        self.message = message
        super().__init__(self.message)
