import bcrypt


class PasswordHandler:
    """
    Класс для обработки паролей с использованием bcrypt.

    Предоставляет методы для хеширования паролей и проверки их соответствия хешу.
    """

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Хеширует пароль с использованием bcrypt.

        Args:
            password: Пароль в виде строки.

        Returns:
            Хешированный пароль в виде строки (декодированный из байтов).
        """
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed_password.decode("utf-8")

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        Проверяет соответствие пароля его хешу.

        Args:
            password: Пароль в виде строки для проверки.
            hashed_password: Хешированный пароль в виде строки.

        Returns:
            True, если пароль соответствует хешу, иначе False.
        """
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))