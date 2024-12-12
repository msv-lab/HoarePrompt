from datetime import date

def calculate_age(birthdate):
    today = date.today()
    age = today.year - birthdate.year
    return age
