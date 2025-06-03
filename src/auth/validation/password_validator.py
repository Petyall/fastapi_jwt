import re

from difflib import SequenceMatcher
from pathlib import Path
from src.config import settings


class PasswordValidator:
    def __init__(self, level: str = settings.PASSWORD_VALIDATION_LEVEL, common_passwords_path: str = settings.PASSWORDS_COMMON_LIST_PATH):
        self.level = level.lower()
        self.common_passwords_path = Path(common_passwords_path) if common_passwords_path else None

    def validate(self, password: str, email: str = ""):
        if self.level == "none":
            return True if password else ["Пароль не может быть пустым"]

        validation_errors = []

        if self.level in ("light", "medium", "strong"):
            validation_errors += self._check_length(password)
            validation_errors += self._check_characters(password)

        if self.level in ("medium", "strong"):
            validation_errors += self._check_similarity(password, email)
            validation_errors += self._check_common_password(password)

        if validation_errors:
            return validation_errors
        
        return True

    def _check_length(self, password: str):
        min_len = 12
        if self.level == "light":
            min_len = 8
        
        if len(password) < min_len:
            return [f"Пароль должен содержать минимум {min_len} символов"]

        return []

    def _check_characters(self, password: str):
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

    def _check_similarity(self, password: str, email: str):
        errors = []
        password = password.lower()

        def is_similar(value: str, label: str):
            value = value.lower()
            part = value.split('@')[0] if '@' in value else value

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

    def _check_common_password(self, password: str):
        if not self.common_passwords_path or not self.common_passwords_path.exists():
            return []

        with self.common_passwords_path.open(encoding='utf-8') as f:
            if password in f.read():
                return ["Пароль слишком распространен"]
        return []

validator = PasswordValidator()
