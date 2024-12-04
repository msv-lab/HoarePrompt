#State of the program right berfore the function call: matrix is a 2D list of integers representing a square matrix of dimension n×n, where n is a positive integer.
def func_1(matrix):
    n = len(matrix)
    total = 0
    for i in range(n):
        total += matrix[i][i]
        
        total += matrix[i][n - i - 1]
        
    #State of the program after the  for loop has been executed: `total` is equal to the sum of the elements on the main diagonal and the secondary diagonal of `matrix`, `matrix` is a 2D list of integers representing a square matrix of dimension n×n where n is a non-negative integer.
    return total
    #The program returns total, which is equal to the sum of the elements on the main diagonal and the secondary diagonal of the matrix, where matrix is a 2D list of integers representing a square matrix of dimension n×n.
#Overall this is what the function does:The function accepts a 2D list of integers representing a square matrix and returns the sum of the elements on both the main diagonal and the secondary diagonal of the matrix. It does not handle the case where the input matrix is not square, which could lead to an IndexError if the dimensions are inconsistent.

