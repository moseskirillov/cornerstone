from dataclasses import dataclass


@dataclass
class CreateUserRequest:
    first_name: str
    last_name: str
    telegram_id: int
    telegram_login: str
