class ScratchApiException(Exception):
    pass


class LoginError(ScratchApiException):
    pass


class ChangePassError(ScratchApiException):
    pass
