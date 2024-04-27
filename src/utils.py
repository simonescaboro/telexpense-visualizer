import os
from datetime import datetime
from pathlib import Path
from typing import Tuple


def get_link_file_path() -> Path:
    path = Path(os.path.join(Path.home(), ".telexpense-viz"))
    return path


def get_icon(title: str):
    return "📉" if title == "expenses" else "📈"


def _r(n: float) -> float:
    return round(n, 2)


def delta(first: float, second: float):
    return _r(first - second)


def get_curr_month_year() -> Tuple[int, int]:
    return datetime.now().month, datetime.now().year


def get_prev_month_year() -> Tuple[int, int]:
    month, year = get_curr_month_year()

    return (month + 11) % 13, year - 1


def _tag(tag: str):
    return f"🏷️ {tag}"


def _untag(tag: str):
    return tag.replace("🏷️", "").strip()


_AMOUNT_FORMAT = "🫰%.2f"
_AMOUNT_PERC_FORMAT = "%.2f ％"
