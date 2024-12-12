import math 
def matrix_diagonal_sum(matrix):
    n = len(matrix)
    total = 0
    for i in range(n):
        total += matrix[i][i]  # Main diagonal
        total += matrix[i][n - i - 1]  # Secondary diagonal
    return total

print(matrix_diagonal_sum([[1, 2, 3], [4, 5, 6], [7, 8, 9]])) # 25