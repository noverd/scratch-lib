class ScratchApiException(Exception):
    pass


class LoginError(ScratchApiException):
    pass


class ChangePassError(ScratchApiException):
    pass


class UserGettingError(ScratchApiException):
    pass


class UnauthorizedError(ScratchApiException):
    pass


class StudioGettingError(ScratchApiException):
    pass