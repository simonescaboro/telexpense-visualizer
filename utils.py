from typing import Tuple
from datetime import datetime


def get_icon(title: str):
    return "📉" if title == "expenses" else "📈"


def _r(n: float) -> float:
    return round(n,2)


def delta(first: float, second: float):
    return _r(first - second)

def get_curr_month_year() -> Tuple[int,int]:
    return datetime.now().month, datetime.now().year
