#State of the program right berfore the function call: matrix is a square 2D list of numbers with dimensions n x n, where n is a positive integer.
def func_1(matrix):
    n = len(matrix)
    total = 0
    for i in range(n):
        total += matrix[i][i]
        
        total += matrix[i][n - i - 1]
        
    #State of the program after the  for loop has been executed: `matrix` is a square 2D list of numbers with dimensions n x n, `total` is equal to the sum of all diagonal and anti-diagonal elements of the matrix, `n` is a non-negative integer.
    return total
    #The program returns total, which is equal to the sum of all diagonal and anti-diagonal elements of the square 2D list 'matrix' with dimensions n x n.
#Overall this is what the function does:The function accepts a square 2D list of numbers, `matrix`, with dimensions n x n, and returns the sum of all diagonal and anti-diagonal elements of the matrix. It does not account for cases where the matrix might be empty or not properly formed as a square matrix, which could lead to unintended behavior.

