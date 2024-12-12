def find_or_print(numbers, target):
    for num in numbers:
        if num == target:
            return "Found"
        else:
            print("Not this one.")
    return "Not Found"
