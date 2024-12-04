#State of the program right berfore the function call: matrix is a 2D list (square matrix) of integers, where the number of rows is equal to the number of columns.
def func_1(matrix):
    n = len(matrix)
    total = 0
    for i in range(n):
        total += matrix[i][i]
        
        total += matrix[i][n - i - 1]
        
    #State of the program after the  for loop has been executed: `total` is equal to the sum of all elements along the primary and secondary diagonals of `matrix`, `matrix` is a 2D list (square matrix) of integers, `n` is a positive integer indicating the size of the matrix.
    return total
    #The program returns the total, which is equal to the sum of all elements along the primary and secondary diagonals of the square matrix of size n.
#Overall this is what the function does:The function accepts a 2D list (square matrix) of integers and returns the sum of all elements along the primary diagonal and the secondary diagonal of the matrix. However, it counts the central element of the matrix twice if the size of the matrix (n) is odd, as it is included in both diagonals. Therefore, if the matrix size is odd, the total will be greater than the actual sum of unique diagonal elements.

