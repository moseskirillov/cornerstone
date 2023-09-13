from dataclasses import dataclass


@dataclass
class AddRequest:
    date: str
    first_name: str
    last_name: str
    telegram: str
    leader_name: str
