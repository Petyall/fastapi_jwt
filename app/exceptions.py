from fastapi import HTTPException, status


# Создание класса для обработки исключений, наследующийся от HTTPException
class ProjectException(HTTPException):
    # Значения по умолчанию
    status_code = 500
    detail = ""
    
    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


# Ошибки по работе с пользователями
class UserAlreadyExistsException(ProjectException):
    status_code=status.HTTP_409_CONFLICT
    detail="Пользователь уже существует"

class UserNotFoundException(ProjectException):
    status_code=status.HTTP_404_NOT_FOUND
    detail="Пользователь не найден"


class UserAlreadyConfirmedException(ProjectException):
    status_code=status.HTTP_409_CONFLICT
    detail="Пользователь уже подтвержден"


class UserIsNotPresentException(ProjectException):
    status_code=status.HTTP_401_UNAUTHORIZED


class NotEnoughAuthorityException(ProjectException):
    status_code=status.HTTP_409_CONFLICT
    detail="У данного пользователя недостаточно прав"


# Ошибки по работе с авторизацией
class TokenExpiredException(ProjectException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Истек срок действия токена"

class TokenAbsentException(ProjectException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Токен отсутствует"

class IncorrectFormatTokenException(ProjectException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Неверный формат токена"

class IncorrectEmailOrPasswordException(ProjectException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Неверная почта или пароль"
