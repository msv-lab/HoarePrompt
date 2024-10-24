from datetime import date
from program import calculate_age

def test_calculate_age():
    birthdate = date(1990, 12, 15)
    today = date(2022, 12, 14)
    assert calculate_age(birthdate) == 31

