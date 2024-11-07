from program import matrix_diagonal_sum

def test_matrix_diagonal_sum():
    matrix = [
        [2, 3, 4],
        [5, 1, 6],
        [7, 8, 9]
    ]
    assert matrix_diagonal_sum(matrix) == 23

test_matrix_diagonal_sum()