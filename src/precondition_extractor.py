import re

# This is the template for the prompt that will be used to extract the precondition.
# It is pretty straight forward
# The user is given a problem description and a program that supposedely solves the problem.
# The LLM is then asked to extract the precondition from the problem description.
# The precondition is then surrounded by double asterisks (**)


PRECONDITION_EXTRACTION_PROMPT_TEMPLATE = """
You are given a programming problem description and a program that solves to this problem. From the problem description, extract a description of the values of the program's input variables and relationship between these variables. We refer to this description as precondition. Print the precondition following the word "Precondition", and surrounded with double asterisks (**). Follow these examples:

# Example 1

Problem description: write a function to find the minimum cost path to reach (m, n) from (0, 0) for the given cost matrix cost[][] and a position (m, n) in cost[][].
Program:
```
R = 3
C = 3
def min_cost(cost, m, n):
	tc = [[0 for x in range(C)] for x in range(R)]
	tc[0][0] = cost[0][0]
	for i in range(1, m+1):
		tc[i][0] = tc[i-1][0] + cost[i][0]
	for j in range(1, n+1):
		tc[0][j] = tc[0][j-1] + cost[0][j]
	for i in range(1, m+1):
		for j in range(1, n+1):
			tc[i][j] = min(tc[i-1][j-1], tc[i-1][j], tc[i][j-1]) + cost[i][j]
	return tc[m][n]
```

Precondition: **cost is a 2D list of non-negative integers, m and n are non-negative integers such that 0 <= m < len(cost) and 0 <= n < len(cost[0]).**

# Example 2

Problem description: Write a function to find the similar elements from the given two tuple lists.
Program:
```
def similar_elements(test_tup1, test_tup2):
  res = tuple(set(test_tup1) & set(test_tup2))
  return (res) 
```

Precondition: **test_tup1 and test_tup2 are tuples.**

# Example 3

Problem description: Write a python function to identify non-prime numbers.
Program:
```
import math
def is_not_prime(n):
    result = False
    for i in range(2,int(math.sqrt(n)) + 1):
        if n % i == 0:
            result = True
    return result
```

Precondition: **n is an integer greater than 1.**

# Example 4

Problem description: Write a function to find the largest integers from a given list of numbers using heap queue algorithm.
Program:
```
import heapq as hq
def heap_queue_largest(nums,n):
  largest_nums = hq.nlargest(n, nums)
  return largest_nums
```

Precondition: **nums is a list of integers, and n is a non-negative integer such that 0 <= n <= len(nums).**

# Example 5

Problem description: Write a function to find the number of ways to fill it with 2 x 1 dominoes for the given 3 x n board.
Program:
```
def count_ways(n):
  A = [0] * (n + 1)
  B = [0] * (n + 1)
  A[0] = 1
  A[1] = 0
  B[0] = 0
  B[1] = 1
  for i in range(2, n+1):
    A[i] = A[i - 2] + 2 * B[i - 1]
    B[i] = A[i - 1] + B[i - 2]
  return A[n] 
```

Precondition: **n is a non-negative integer.**

# Your task

Problem description: {description}
Program:
```
{program}
```

"""

def extract_precondition_from_response(response_content):
    pattern = r"Precondition:\s*\*\*(.*?)\*\*|Precondition:\s*(.*)"
    match = re.search(pattern, response_content)
    if match:
        if match.group(1):
            return match.group(1).strip()
        elif match.group(2):
            return match.group(2).strip()
    return response_content


def default(model, description, program):
    prompt = PRECONDITION_EXTRACTION_PROMPT_TEMPLATE.format(program=program, description=description)
    response = model.query(prompt)
    return extract_precondition_from_response(response)
    
