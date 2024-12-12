#State of the program right berfore the function call: matrix is a 2D list representing a square matrix of dimensions n x n, where n is a positive integer.
def func_1(matrix):
    n = len(matrix)
    total = 0
    for i in range(n):
        total += matrix[i][i]
        
        total += matrix[i][n - i - 1]
        
    #State of the program after the  for loop has been executed: `total` is equal to the sum of all diagonal elements of the matrix, `matrix` is a 2D list representing a square matrix of dimensions `n x n` where `n` is a positive integer, `total` includes elements `matrix[i][i]` and `matrix[i][n - i - 1]` for all `i` from 0 to `n-1`.
    return total
    #The program returns total, which is equal to the sum of all diagonal elements of the matrix, including elements matrix[i][i] and matrix[i][n - i - 1] for all i from 0 to n-1.
#Overall this is what the function does:The function accepts a 2D list `matrix` representing a square matrix of dimensions n x n and returns the sum of all diagonal elements from both the main diagonal and the secondary diagonal. If n is 1 (a 1x1 matrix), the function will return the single element as it will be counted in both diagonals. However, if the matrix is not square or contains non-numeric types, the function's behavior is not defined as there are no checks for input validity.

