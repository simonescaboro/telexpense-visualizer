from src.utils import get_prev_month_year
import random


def test_prev_month_year():
    years = [2000+i for i in range(-10,50)]
    months = [random.randint(1,12) for _ in range(-10,50)]

    for month, year in zip(months, years):
        prev_m, prev_y = get_prev_month_year(month, year)
        if month == 1:
            assert (month == 1 and prev_m == 12 and prev_y == year-1), f"{month=},{year=},{prev_m=},{prev_y}"
        else:
            assert prev_y == year-1 and month-1 == prev_m and prev_m > 0, f"{month=},{year=},{prev_m=},{prev_y}"
