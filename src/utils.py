import os
from datetime import datetime
from pathlib import Path
from typing import Tuple, Dict, Optional


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


def get_prev_month_year(
        curr_month: Optional[int] = None,
        curr_year: Optional[int] = None
    ) -> Tuple[int, int]:
    month, year = get_curr_month_year()

    if curr_month:
        month = curr_month
    if curr_year:
        year = curr_year

    return (month - 2) % 12 + 1, year - 1


def _tag(tag: str):
    return f"🏷️ {tag}"


def _untag(tag: str):
    return tag.replace("🏷️", "").strip()

def get_month_name_idx_map() -> Dict[str,int]:
    return {
        "genuary": 1,
        "february": 2,
        "march": 3,
        "april": 4,
        "may": 5,
        "june": 6,
        "july": 7,
        "august": 8,
        "september": 9,
        "october": 10,
        "november": 11,
        "december": 12,
    }


def get_month_name(idx: int) -> str:
    map = get_month_name_idx_map()
    map = {v:k for k,v in map.items()} 
    return map[idx]


def get_month_idx(month: str) -> int:
    map = get_month_name_idx_map()
    return map[month]


_AMOUNT_FORMAT = "🫰%.2f"
_AMOUNT_PERC_FORMAT = "%.2f ％"
