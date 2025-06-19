import re
from difflib import SequenceMatcher
from pathlib import Path

from src.config import settings


class PasswordValidator:
    """
    Класс для валидации паролей на основе заданного уровня строгости.

    Проверяет длину, наличие символов, схожесть с email и использование распространённых паролей.
    Уровни валидации: none, light, medium, strong.
    """
    VALID_LEVELS = {"none", "light", "medium", "strong"}

    def __init__(self, level: str = settings.PASSWORD_VALIDATION_LEVEL, common_passwords_path: str = settings.PASSWORDS_COMMON_LIST_PATH):
        """
        Инициализирует валидатор паролей.

        Args:
            level: Уровень строгости валидации пароля (none, light, medium, strong).
            common_passwords_path: Путь к файлу со списком распространённых паролей.

        Raises:
            ValueError: Если указан недопустимый уровень валидации.
        """
        self.level = level.lower()
        if self.level not in self.VALID_LEVELS:
            raise ValueError(f"Недопустимый уровень проверки пароля: {self.level}")

        self.common_passwords_path = Path(common_passwords_path) if common_passwords_path else None
        self._common_passwords = set()

        if self.common_passwords_path and self.common_passwords_path.exists():
            try:
                with self.common_passwords_path.open(encoding="utf-8") as f:
                    self._common_passwords = {line.strip() for line in f if line.strip()}
            except Exception:
                print("/src/validation/password_validator.py - Файл с популярными паролями не найден, инициаилизировано пустое множество...")
                self._common_passwords = set()

    def validate(self, password: str, email: str = "") -> bool | list[str]:
        """
        Проверяет пароль на соответствие требованиям выбранного уровня валидации.

        Args:
            password: Пароль для проверки.
            email: Email пользователя для проверки схожести (опционально).

        Returns:
            True, если пароль соответствует требованиям, иначе список ошибок валидации.
        """
        if self.level == "none":
            return True if password else ["Пароль не может быть пустым"]

        validation_errors = []

        if self.level in ("light", "medium", "strong"):
            validation_errors += self._check_length(password)
            validation_errors += self._check_characters(password)

        if self.level in ("medium", "strong"):
            validation_errors += self._check_similarity(password, email)
            validation_errors += self._check_common_password(password)

        return validation_errors if validation_errors else True

    def _check_length(self, password: str) -> list[str]:
        """
        Проверяет минимальную длину пароля в зависимости от уровня валидации.

        Args:
            password: Пароль для проверки.

        Returns:
            Список ошибок, если длина пароля недостаточна, иначе пустой список.
        """
        min_len = 12 if self.level != "light" else 8
        if len(password) < min_len:
            return [f"Пароль должен содержать минимум {min_len} символов"]
        return []

    def _check_characters(self, password: str) -> list[str]:
        """
        Проверяет наличие букв, цифр и, для уровней medium/strong, спецсимволов.
        Для уровня strong дополнительно проверяет наличие строчных и заглавных букв.

        Args:
            password: Пароль для проверки.

        Returns:
            Список ошибок, если пароль не содержит требуемые символы, иначе пустой список.
        """
        errors = []
        if not re.search(r"[A-Za-z]", password):
            errors.append("Пароль должен содержать хотя бы одну букву")
        if not re.search(r"\d", password):
            errors.append("Пароль должен содержать хотя бы одну цифру")

        if self.level in ("medium", "strong"):
            if not re.search(r"[!@#$%^&*()_+\-=\[\]{};:\\|,.<>/?~]", password):
                errors.append("Пароль должен содержать хотя бы один спецсимвол")

        if self.level == "strong":
            if not re.search(r"[a-z]", password):
                errors.append("Пароль должен содержать хотя бы одну строчную букву")
            if not re.search(r"[A-Z]", password):
                errors.append("Пароль должен содержать хотя бы одну заглавную букву")

        return errors

    def _check_similarity(self, password: str, email: str) -> list[str]:
        """
        Проверяет, не слишком ли пароль похож на email пользователя.
        Использует SequenceMatcher для оценки схожести строк (порог 0.7).

        Args:
            password: Пароль для проверки.
            email: Email пользователя для сравнения.

        Returns:
            Список ошибок, если пароль совпадает или слишком похож на email, иначе пустой список.
        """
        errors = []
        password = password.lower()

        def is_similar(value: str, label: str):
            value = value.lower()
            part = value.split("@")[0] if "@" in value else value

            if password == part:
                return f"Пароль не должен совпадать с {label}"
            if part in password:
                return f"Пароль не должен содержать {label} как подстроку"
            if SequenceMatcher(None, part, password).ratio() > 0.7:
                return f"Пароль слишком похож на {label}"
            return None

        for check_value, label in [(email, "email")]:
            if check_value:
                msg = is_similar(check_value, label)
                if msg:
                    errors.append(msg)

        return errors

    def _check_common_password(self, password: str) -> list[str]:
        """
        Проверяет, не является ли пароль распространённым.

        Args:
            password: Пароль для проверки.

        Returns:
            Список ошибок, если пароль найден в списке распространённых, иначе пустой список.
        """
        if password in self._common_passwords:
            return ["Пароль слишком распространен"]
        return []


validator = PasswordValidator()
