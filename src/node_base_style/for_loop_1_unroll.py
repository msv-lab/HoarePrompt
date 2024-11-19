import ast

from node_base_style.hoare_triple import pprint_cmd, Triple
from node_base_style.helper import extract_result


# The prompt template instructs the model on how to analyze the state of the loop after several(k) iterations.
LOOP_PROMPT = """
You have been assigned the role of a program verifier, responsible for analyzing the program's state after the for loop. The initial state of the code has already been provided. Additionally, you can see how the state changes after the loop executes 1 time. The initial state includes the values and relationships of the variables before the program execution. The output state should include the values and relationships of the variables after all the iterations of the for loop have executed. Similar to the initial state, avoid explaining how the program operates; focus solely on the variable values and their interrelations. 
You must adhere to the text format: Output State: **output state.**
I am giving you two examples to understand the task better. Then I am giving you your task.

Example 1: 

Initial State: `n` is a non negative  integer, `factorial` is 1.
Code of the loop:
```
for i in range(1, n + 1):
    factorial *= i
```
Output state after the loop executes 1 times:  `factorial` is `1`, 'i' is 1 , n is at least 1.

Now, please think step by step. Using the results from the first few iterations of the loop provided in the example as hints but  mostly from the loop code, determine the loop's output state.

Example Answer 1:
If n is greater than 0 the loop will execute at least once and factorial will contain the factorial of n and i will be n. If n is 0  then the loop wont execute and factorial will remain 1 which is indeed the factorial for 0.
Therefore, the output state of the loop is that `factorial` is the factorial of `n`
Output State: **``n` is a non negative  integer, `factorial` is the factorial of 'n'**

Example 2: 

Initial State:  `total` is 0,'students_num' is 0, students is a list of students.
Code of the loop:
```
for student in students:
    total += student
    students_num += 1
```
Output State after the loop executes 1 times:  `total` is equal to the first student, 'students_num' is 1, students is a list with at least one student, student is the first student in the list.


Now, please think step by step. Using the results from the first few iterations of the loop provided in the example as hints but  mostly from the loop code, determine the loop's output state.

Example Answer 2:
The loop calculates the sum of a list students and stores it in total and the number of students in students_num. The loop will be executed at least once if students is a list with at least one student. If the list is empty the loop does not execute and total and students_num are 0.
Output State: **total is equal to the sum of all students, students_num is the number of students, students is a list of students.**
Your Task:

Initial State: {pre}
Code of the loop:
```
{loop_code}
```
{loop_unrolled}

Now, please think step by step. Use the results from the first iteration of the loop provided in the example to help you , but mostly focus on the loop code to determine the loop's output state after ALL THE ITERATIONS OF THE LOOP HAVE FINISHED. Try to understand what  will be the values of the variables after it executes. In the case the loop doesnot execute, what will be the values of the variables.
Use the fomrat Output State: **the output state you calculate**
"""

# Format examples of loop iterations into the text format required for the prompt.
# This will show multiple iterations of a loop and how the state changes.the loop k unrolled
def format_examples(examples: list[Triple]):
    s = ""
    i = 1
    for e in examples:
        post = e.postcondition
        s = s + f"Output State after the loop executes {i} times: {post}\n"
        i += 1
    return s

# The model will compute the final state of the program after multiple iterations of the loop.
def complete_for_triple_1_unroll(incomplete_triple: Triple, model, examples: list[Triple]):
    
    loop_unrolled = format_examples(examples)
    prompt = LOOP_PROMPT.format(loop_unrolled=loop_unrolled, pre=incomplete_triple.precondition,
                                loop_code=pprint_cmd(incomplete_triple.command))
    response = model.query(prompt)
    post = extract_result(response, "Output State")
    return post

# Retrieve the head of a while loop, which is its condition 
def get_while_head(node: ast.While) -> str:
    condition = ast.unparse(node.test)
    while_head = f"while {condition}:"
    return while_head

# Retrieve the head of a for loop, which includes the loop variable and iterable
def get_for_loop_head(node: ast.For) -> str:
    loop_var = ast.unparse(node.target)  # Loop variable (e.g., `x` in `for x in y`)
    iter_expr = ast.unparse(node.iter)   # Iterable expression (e.g., `y` in `for x in y`)
    for_head = f"for {loop_var} in {iter_expr}:"
    return for_head


# This class transforms a for loop into a while loop
class ForToWhileTransformer(ast.NodeTransformer):
    def visit_For(self, node):
        # If the for loop is iterating over a range, we transform it into a while loop
        if isinstance(node.iter, ast.Call) and isinstance(node.iter.func, ast.Name) and node.iter.func.id == 'range':
            args = node.iter.args 
            start = args[0] if len(args) > 0 else ast.Constant(value=0) #start of the range
            stop = args[1] if len(args) > 1 else ast.Constant(value=0) #end of the range
            step = args[2] if len(args) > 2 else ast.Constant(value=1) #step of the range
            # Case of a simple range loop with constant values
            if len(args) < 3 or (isinstance(start, ast.Constant) and isinstance(stop, ast.Constant) and isinstance(step,
                                                                                                                   ast.Constant)):
                init = ast.Assign(targets=[node.target], value=start)
                if isinstance(step, ast.UnaryOp) and isinstance(step.op, ast.USub):
                    comp_op = ast.Gt()
                else:
                    comp_op = ast.Lt()
                condition = ast.Compare(left=node.target, ops=[comp_op], comparators=[stop])

                self.generic_visit(node)

                increment = ast.AugAssign(target=node.target, op=ast.Add(), value=step)
                node.body.append(increment)
                while_node = ast.While(test=condition, body=node.body, orelse=node.orelse)
                return [init, while_node]
            # Case of a more complex loop
            else:
                target = node.target
                # Instead of directly looping over the sequence, the code creates an explicit iterator using the built-in iter function
                # Then a try catch block is used to handle the StopIteration exception
                iter_var = ast.Name(id=f'iter_{target.id}', ctx=ast.Store())
                iter_init = ast.Assign(
                    targets=[iter_var],
                    value=ast.Call(
                        func=ast.Name(id='iter', ctx=ast.Load()),
                        args=[node.iter],
                        keywords=[]
                    )
                )
                self.generic_visit(node)

                try_except = ast.Try(
                    body=[
                             ast.Assign(
                                 targets=[target],
                                 value=ast.Call(
                                     func=ast.Name(id='next', ctx=ast.Load()),
                                     args=[iter_var],
                                     keywords=[]
                                 )
                             )
                         ] + node.body,
                    handlers=[
                        ast.ExceptHandler(
                            type=ast.Name(id='StopIteration', ctx=ast.Load()),
                            name=None,
                            body=[ast.Break()]
                        )
                    ],
                    orelse=[],
                    finalbody=[]
                )
                while_node = ast.While(test=ast.Constant(value=True), body=[try_except], orelse=node.orelse)
                return [iter_init, while_node]
        # Case of other non-range iterators like lists
        else:
            iter_var = ast.Name(id='iterator', ctx=ast.Store())
            iter_init = ast.Assign(targets=[iter_var],
                                   value=ast.Call(func=ast.Name(id='iter', ctx=ast.Load()), args=[node.iter],
                                                  keywords=[]))

            self.generic_visit(node)

            try_except = ast.Try(
                body=[ast.Assign(targets=[node.target],
                                 value=ast.Call(func=ast.Name(id='next', ctx=ast.Load()), args=[iter_var],
                                                keywords=[]))] + node.body,
                handlers=[ast.ExceptHandler(type=ast.Name(id='StopIteration', ctx=ast.Load()), name=None,
                                            body=[ast.Break()])],
                orelse=[],
                finalbody=[]
            )

            while_node = ast.While(test=ast.Constant(value=True), body=[try_except], orelse=node.orelse)
            return [iter_init, while_node]

# This is a test to test the transformation logic for for-loops
if __name__ == "__main__":
    code = """
for i in range(2, n + 1):
    prev, curr = curr, prev * curr
for i in range(a, b, c):
    print(i)
for j in some_iterable:
    print(j)
for i in matrix:
    for j in i:
        print(j)
for i, j in zip(xs, ys):
    print(i)
    """
    parsed_code = ast.parse(code)

    transformer = ForToWhileTransformer()
    transformed_code = transformer.visit(parsed_code)

    transformed_code = ast.fix_missing_locations(transformed_code)
    final_code = ast.unparse(transformed_code)

    print(final_code)
