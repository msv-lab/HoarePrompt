def func_1(matrix):
    n = len(matrix)
    total = 0
    for i in range(n):
        total += matrix[i][i]
        total += matrix[i][n - i - 1]
    return total
print(func_1([[1, 2, 3], [4, 5, 6], [7, 8, 9]]))