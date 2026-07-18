class ApplicationError(Exception):
    pass


class UserNotFoundError(ApplicationError):
    pass


class LoginAlreadyExistsError(ApplicationError):
    pass


class PasswordTooShortError(ApplicationError):
    pass


class InvalidCredentialsError(ApplicationError):
    pass


class PasswordEntryNotFoundError(ApplicationError):
    pass
