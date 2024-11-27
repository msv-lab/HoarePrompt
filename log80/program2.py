def test(my_list):
    if len(my_list) % 2 == 0:
        return 0
    if len(my_list)>=3:
        return 0
    return my_list[1]