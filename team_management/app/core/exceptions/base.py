class AppException(Exception):
    def __init__(self, msg: str | None = None):
        self.msg = msg
