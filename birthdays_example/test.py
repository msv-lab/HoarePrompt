from program import calculate_age
from datetime import date

def test_calculate_age():
    # Future birthdate
    future_birthdate = date.today().replace(year=date.today().year + 1)
    assert calculate_age(future_birthdate) < 0

    # Invalid birthdate (February 30th)
    invalid_birthdate = date(date.today().year, 2, 30)
    assert calculate_age(invalid_birthdate) is None

