import bcrypt
from src.config import settings


class PasswordHandler:
    """
    Класс для обработки паролей с использованием bcrypt.

    Предоставляет методы для хеширования паролей и проверки их соответствия хешу.
    """

    def __init__(self, salt_rounds: int = settings.PASSWORD_BCRYPT_SALT_ROUNDS):
        self.salt_rounds = salt_rounds

    def hash_password(self, password: str) -> str:
        """
        Хеширует пароль с использованием bcrypt.

        Args:
            password: Пароль в виде строки.

        Returns:
            Хешированный пароль в виде строки (декодированный из байтов).
        """
        salt = bcrypt.gensalt(rounds=self.salt_rounds)
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed_password.decode("utf-8")

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        Проверяет соответствие пароля его хешу.

        Args:
            password: Пароль в виде строки для проверки.
            hashed_password: Хешированный пароль в виде строки.

        Returns:
            True, если пароль соответствует хешу, иначе False.
        """
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

password_handler = PasswordHandler()
