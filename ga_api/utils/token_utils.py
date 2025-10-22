from secrets import choice
from string import ascii_letters, digits


class TokenUtils:
    @staticmethod
    def generate_random_password(length: int = 8) -> str:
        safe_chars = ascii_letters + digits + "!@#$%^&*()-_=+"
        return "".join(choice(safe_chars) for _ in range(length))
