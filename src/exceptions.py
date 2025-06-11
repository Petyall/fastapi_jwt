from fastapi import HTTPException, status


class ProjectException(HTTPException):
    status_code = 500
    detail = "Внутренняя ошибка сервера"
    expose_to_client: bool = True

    def __init__(self, detail: str = None, expose_to_client: bool = True):
        if detail:
            self.detail = detail
        self.expose_to_client = expose_to_client
        super().__init__(status_code=self.status_code, detail=self.detail)


class UserAlreadyExistsException(ProjectException):
    status_code = status.HTTP_409_CONFLICT

    def __init__(self, user_email: str):
        super().__init__(detail=f"Пользователь '{user_email}' уже существует")


class UserNotFoundException(ProjectException):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, user_email: str):
        super().__init__(detail=f"Пользователь '{user_email}' не найден")


class UserHasNoRightsException(ProjectException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Недостаточно прав"


class PasswordValidationErrorException(ProjectException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, validation_result: str):
        super().__init__(detail=f"Пароль не соответствует требованиям:\n{validation_result}")


class PasswordIdenticalToPreviousException(ProjectException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Новый пароль должен отличаться от предыдущего"


class InvalidPasswordResetTokenException(ProjectException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Токен недействителен"


class InternalServerErrorException(ProjectException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, reason: str = "Ошибка на сервере. Попробуйте позже."):
        super().__init__(detail=reason, expose_to_client=False)


class InvalidCredentialsException(ProjectException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "email или пароль введены неправильно"


class RefreshTokenNotFoundException(ProjectException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Refresh-токен не найден"


class InvalidRefreshTokenException(ProjectException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Refresh-токен недействителен"


class AccessTokenNotFoundException(ProjectException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Access-токен не найден"


class InvalidAccessTokenException(ProjectException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Access-токен недействителен"


class InvalidOrExpiredEmailTokenException(ProjectException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Ссылка недействительна или устарела"


class EmailAlreadyConfirmedException(ProjectException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Вы уже подтвердили свою почту!"


class TooEarlyResendException(ProjectException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    detail="Письмо уже было отправлено недавно. Попробуйте позже"