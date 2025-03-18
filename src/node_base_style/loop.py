import ast
import re
from node_base_style.hoare_triple import pprint_cmd, Triple
# from node_base_style.helper import extract_result
LOOP_PROMPT = """
Given a Python loop, an initial execution state, and the output states after the first {times} iterations of the loop, determine the output state after all the executions of the loop have finished.

You must adhere to the text format: Output State: **output state.**

Initial State: {pre}
Code of the loop:
{loop_code}

The output state after the loop executes the first {times} times includes what needed to be true for the loop to execute at least that number of times:
{loop_unrolled}

What is the ouput state after the loop executes all the iterations? Change the values of only the variables in the loop head and body.The state of the other variables in the precondition that are not affected by the loop head and body must remain unchanged.
In your response strictly use the format: Output State: **the output state you calculate.**, and describe this output state in Natural language easily understandable by humans.

"""

LOOP_PROMPT_0_UNROLL= """
Given a Python loop and an initial execution state, determine the output state after all the executions of the loop have finished.

You must adhere to the text format: Output State: **output state.**

Initial State: {pre}
Code of the loop:
{loop_code}


What is the ouput state after the loop executes all the iterations? Change the values of only the variables in the loop head and body.The state of the other variables in the precondition that are not affected by the loop head and body must remain unchanged.
In your response strictly use the format: Output State: **the output state you calculate.**, and describe this output state in Natural language easily understandable by humans.

"""
# The prompt template instructs the model on how to analyze the state of the loop after several(k) iterations.
# LOOP_PROMPT = """
# ou have been assigned the role of a program verifier, responsible for analyzing the program's state after the while loop. The initial state of the code has already been provided. Additionally, you can see how the state changes after the loop executes a few times. 
# In the information given, the output state after the loop executes some number of times include what needed to be true for the loop to execute at least that number of times. 
# The initial state includes the values and relationships of the variables before the program execution. The output state should include the values and relationships of the variables after all the iterations of the while loop have executed. Similar to the initial state, avoid explaining how the program operates; focus solely on the variable values and their interrelations. 
# You must adhere to the text format: Output State: **output state.**
# I am giving you two examples to understand the task better. Then I am giving you your task.

# Example 1: 

# Initial State: `n` is a positive integer, `factorial` is 1
# Code of the loop:
# ```
# while n > 0:
#     factorial *= n
#     n -= 1
# ```

# Output State after loop executes 1 times:  n must initially be greater than 0, `factorial` is `n`, `n` is decremented to `n-1`.
# Output State after loop executes 2 times: `factorial` is `n * (n - 1)`, `n` is decremented to `n-2`, initial `n` must have been greater than 1
# Output State after loop executes 3 times: `factorial` is `n * (n - 1) * (n - 2)`, `n` is decremented to `n-3`, initial `n` must have been  had greater than 2.
# Now, please think step by step. Using the results from the first few iterations of the loop provided in the example as hints but  mostly from the loop code, determine the loop's output state.

# Example Answer 1:
# if n is greater than 0 the loop will execute at least once and fac will contain the factorial of n and n will be 0. If n is 0 then the loop wont execute and fac will remain 1, which is indeed the factorial of 0 , and the value of n wont change.
# Therefore, the output state of the loop is that `fac` is the factorial of the original value of `n`, 'n' is 0.
# Output State: **n` is 0, `fac` is the factorial of the original value of 'n' **

# Example 2: 

# Initial State:  `total` is 0, 'students' can hold any value. 
# Code of the loop:
# ```
# while students >= 1:
#     total += students
#     students -= 1
# ```

# Output state after loop executes 1 time: `total` is equal to the initial value of 'students', 'students' becomes 1 less than the initial value of 'students', inital value of students must have been greater than 0
# Output state after loop executes 2 times: `total` is equal to twice the initial value of 'students' minus 1, 'students' becomes 2 less than the initial value of 'students', initial value of students must have been greater than 1
# Output state after loop executes 3 times: `total` is equal to three times the initial value of 'students' minus 3, 'students' becomes 3 less than the initial value of 'students', initial value of students must have been greater than 2

# Now, please think step by step. Using the results from the first few iterations of the loop provided in the example as hints but  mostly from the loop code, determine the loop's output state.

# Example answer 2:
# The loop calculates the sum of all numbers from 1 to students and stores it in total . The loop will be executed at least once if students is greater or equal to 1 and in the end students will be 0. if students is less thn 1 then the loop will not execute and the value of total will remain 0.
# Output State: **'students' is 0, if students was initially greater or equal to 1 then total` is the sum of all numbers from 1 to the initial value of students, if students is less than 1 the loop doesnt execute and total is 0**
# Your Task:

# Initial State: {pre}
# Code of the loop:
# ```
# {loop_code}
# ```

# The output state after the loop executes some number of times include what needed to be true for the loop to execute at least that number of times. 

# {loop_unrolled}
# Now, please think step by step. Using the results from the first few iterations of the loop provided in the example, determine the loop's output state, after all the iterations of the loop have executed. Make sure to include the values of the variables after the loop has finished especially the any loop control variables. 
# If the state of some variables is dependant on earlier or the oginal value of some variable, make sure to seprate the original value from the current value.
# Use the fomrat Output State: **the output state you calculate**
# """

# Format examples of loop iterations into the text format required for the prompt.
# This will show multiple iterations of a loop and how the state changes.the loop k unrolled

def extract_result(s: str, keyword: str):
    pattern = fr"{keyword}:\s*\*\*(.*?)\*\*"
    matches = re.findall(pattern, s, re.DOTALL)
    if matches:
        # Select the last match
        res = matches[-1]
        # Clean up the beginning and end of the string for any weird characters like * or newlines
        return res.strip(), True
    return s, False


def format_examples(examples: list[Triple]):
    s = ""
    i = 1
    for e in examples:
        post = e.postcondition
        if i == 1:
            s = s + f"Output State after the loop executes {i} time: {post}\n"
        else:
            s = s + f"Output State after the loop executes {i} times: {post}\n"
        i += 1
    return s, i-1
# The model will compute the final state of the program after multiple iterations of the loop.
def complete_loop_triple(incomplete_triple: Triple, model, examples: list[Triple], retry= True):
    
    loop_unrolled, times = format_examples(examples)
    prompt = LOOP_PROMPT.format(loop_unrolled=loop_unrolled, pre=incomplete_triple.precondition,
                                loop_code=pprint_cmd(incomplete_triple.command), times=times)
    response = model.query(prompt)
    post, found= extract_result(response, "Output State")
    if retry and not found:
        return complete_loop_triple(incomplete_triple, model, examples, retry=False)
    return post

def complete_loop_triple_0_unroll(incomplete_triple: Triple, model, retry= True):
    
    
    prompt = LOOP_PROMPT_0_UNROLL.format( pre=incomplete_triple.precondition,
                                loop_code=pprint_cmd(incomplete_triple.command))
    response = model.query(prompt)
    post, found= extract_result(response, "Output State")
    if retry and not found:
        return complete_loop_triple_0_unroll(incomplete_triple, model, retry=False)
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
