import re

from node_base_style.hoare_triple import LoopTriple, pprint_cmd, Triple

LOOP_PROMPT = """
You have been assigned the role of a program verifier, responsible for analyzing the program's state after the loop. The initial state of the code has already been provided. Additionally, you can see examples of the loop executing several times. The initial state includes the values and relationships of the variables before the program execution. The output state should include the values and relationships of the variables after the execution of the loop. Similar to the initial state, avoid explaining how the program operates; focus solely on the variable values and their interrelations. You must adhere to the text format: Output State: **output state.**

Example: 
Loop executes 1 time:
Initial State: `factorial` is 1, n is a positive integer.
```
factorial *= n
n -= 1
```
Output State: `factorial` is `n`, `n` is decremented to `n-1`.

Loop executes 2 time:
Initial State: `factorial` is `n`, `n` is decremented to `n-1`, `n` is greater then 1.
```
factorial *= n
n -= 1
```
Output State: `factorial` is `n * (n - 1)`, `n` is decremented to `n-2`, `n` is greater then 1.

Loop executes 3 time:
Initial State: `factorial` is `n * (n - 1)`, `n` is decremented to `n-2`, `n` is greater then 2.
```
factorial *= n
n -= 1
```
Output State: `factorial` is `n * (n - 1) * (n - 2)`, `n` is decremented to `n-3`, `n` is greater then 2.


The following provides the initial state of the loop and the loop's code.
Initial State: `n` is a positive integer, `factorial` is 1.
```
while n > 0:
    factorial *= n
    n -= 1
```
Now, please think step by step. Using the results from the first few iterations of the loop provided in the example, determine the loop's output state.

Example Answer:
`n` is a positive integer, so the loop will be executed at least once. After 1 iteration, factorial is `n`, and `n` is decremented to n-1.
If `n` is greater than 1, the loop will be executed at least twice. After 2 iterations, factorial is `n * (n - 1)`, and `n` is decremented to `n-2`.
If `n` is greater than 2, the loop will be executed at least three times. After 3 iterations, factorial is `n * (n - 1) * (n - 2)`, and `n` is decremented to `n-3`.
Therefore, the output state of the loop is that `factorial` is the factorial of `n`, and `n` is decremented to 0.
Output State: **`factorial` is the factorial of `n`, and `n` is decremented to 0.**

Your Task:
Example: 
{loop_unrolled}

The following provides the initial state of the loop and the loop's code.
Initial State: {pre}
```
{loop_code}
```
Now, please think step by step. Using the results from the first few iterations of the loop provided in the example, determine the loop's output state.
"""


def format_examples(examples: list[Triple]):
    s = ""
    i = 1
    for e in examples:
        pre = e.precondition
        code = pprint_cmd(e.command.body)
        post = e.postcondition
        s = s + f"Loop executes {i} time:" + "\n" + f"Initial State: {pre}" + "\n```\n" + code + "\n```\n" + f"Output State: {post}" + "\n\n"
        i += 1
    return s

def complete_loop_triple(incomplete_triple: LoopTriple, model, examples: list[Triple]):
    loop_unrolled = format_examples(examples)
    prompt = LOOP_PROMPT.format(loop_unrolled=loop_unrolled, pre=incomplete_triple.precondition, loop_code=pprint_cmd(incomplete_triple.command))
    response = model.query(prompt)
    post = extract_postcondition(response)
    print("*" * 50)
    print(incomplete_triple)
    print(f"LLM post: {post}")
    return post


def extract_postcondition(s: str) -> str:
    pattern = r"Output State:\s*\*\*(.*?)\*\*"
    match = re.search(pattern, s, re.DOTALL)
    if match:
        return match.group(1)
    return s
