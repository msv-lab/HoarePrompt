#State of the program right berfore the function call: matrix is a 2D list representing a square matrix of integers, where the number of rows is equal to the number of columns (i.e., len(matrix) == len(matrix[0])).
def func_1(matrix):
    n = len(matrix)
    total = 0
    for i in range(n):
        total += matrix[i][i]
        
        total += matrix[i][n - i - 1]
        
    #State of the program after the  for loop has been executed: `total` is equal to the sum of all elements along both the main diagonal and the anti-diagonal of `matrix`; `n` is a non-negative integer, `matrix` is a 2D list representing a square matrix of integers.
    return total
    #The program returns total, which is equal to the sum of all elements along both the main diagonal and the anti-diagonal of the square matrix `matrix`.
#Overall this is what the function does:The function accepts a square matrix of integers and returns the sum of all elements along both the main diagonal and the anti-diagonal. However, it counts the center element twice in case of an odd-sized matrix, which means the actual sum may be greater than expected if the matrix size is odd.

