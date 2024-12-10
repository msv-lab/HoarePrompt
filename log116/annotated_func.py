#State of the program right berfore the function call: matrix is a 2D list representing a square matrix of dimensions n×n, where n is a positive integer.
def func_1(matrix):
    n = len(matrix)
    total = 0
    for i in range(n):
        total += matrix[i][i]
        
        total += matrix[i][n - i - 1]
        
    #State of the program after the  for loop has been executed: `matrix` is a 2D list representing a square matrix of dimensions n×n; `n` is a positive integer; `total` is equal to the sum of the diagonal and anti-diagonal elements of `matrix`; `i` is `n - 1`.
    return total
    #The program returns the total, which is equal to the sum of the diagonal and anti-diagonal elements of the square matrix of dimensions n×n.
#Overall this is what the function does:The function accepts a 2D list `matrix` representing a square matrix of dimensions n×n, where n is a positive integer, and returns the sum of the diagonal and anti-diagonal elements of the matrix. It does not handle cases where the input is not a square matrix or when the matrix is empty, which may lead to unexpected behavior or errors.

