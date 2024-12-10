#State of the program right berfore the function call: matrix is a 2D list (square matrix) of integers, where the number of rows is equal to the number of columns.
def func_1(matrix):
    n = len(matrix)
    total = 0
    for i in range(n):
        total += matrix[i][i]
        
        total += matrix[i][n - i - 1]
        
    #State of the program after the  for loop has been executed: `total` is equal to the sum of all elements from the main diagonal and the anti-diagonal of `matrix`, `n` is a non-negative integer, if `n` is greater than 0 then `total` is the sum involving `n` elements, else `total` is 0.
    return total
    #The program returns the value of total, which is equal to the sum of all elements from the main diagonal and the anti-diagonal of the matrix, or 0 if n is not greater than 0.
#Overall this is what the function does:The function accepts a 2D list `matrix` that represents a square matrix of integers and returns the sum of the elements from the main diagonal and the anti-diagonal. If the matrix is empty (i.e., has no rows), it returns 0. Note that for a matrix of odd size, the center element is counted twice, which may lead to an unexpected increase in the total sum.

