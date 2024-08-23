from node_base_style.hoare_triple import LoopTriple, parse_stmt, State
from node_base_style.helper import extract_postcondition, format_prompt

VERIFYER_SYSTEM_PROMPT_LOOP = """You are assigned the role of a program verifier, responsible for completing the overall Hoare triples for loop statements. In addition to the Hoare triples, you will also see the postcondition of the loop body. You need to combine the precondition, the code, and the postcondition of the loop body to infer the overall postcondition of the loop. Each Hoare triple is made up of three components: a precondition, a program fragment, and a postcondition. The precondition and the postcondition are expressed in natural language. The postcondition of the loop body records how the loop body code changes the state of the variables in a single iteration.

Precondition: describes the initial state of the program variables before the execution of the program fragment. This description should only include the values of the variables, without detailing the operational aspects of the program.

Program Fragment: This is a given part of the task and is not something you need to create or modify. If the loop is a for loop, new variables may appear. If the loop is a while loop, and the condition correctness needs to be determined, you need to discuss both entering and not entering the loop.

Postcondition: describes the state of the program variables after the execution of the program fragment with the initial state described in the precondition. This description should include both the values of the variables and the relationships between them. Similar to the precondition, avoid explaining how the program operates; concentrate solely on the variable values and their interrelations. Ensure that the postcondition retains the conditions stated in the precondition. You need to strictly follow the format."""

generic_while_ctx = [
    LoopTriple(
        "`n` is 5, `factorial` is 1",
        parse_stmt('''
while n > 0:
    factorial *= n
    n -= 1
    '''),
        "`factorial` is updated to its previous value multiplied by `n`, and `n` is decremented by 1.",
        "`n` is 0 and variable `factorial` holds the value of the factorial of 5, which is 120."
    ),
    LoopTriple(
        State.TOP,
        parse_stmt('''
while i * i <= n:
    i += 1
    '''),
        "`i` is increased by 1",
        "If `i` squared is greater than `n` before the loop, `i` remains unchanged. If `i` squared is less than or equal to `n`, `i` increments by 1 each iteration. After the loop, `i` is the smallest integer whose square is strictly greater than `n`."
    ),
    LoopTriple(
        "`string` is a string, `index` is the length of string minus 1, `reversed_string` is an empty string",
        parse_stmt("""
while index >= 0:
    reversed_string += string[index]
    index -= 1
        """),
        "`reversed_string` appends the character at index `index` of the variable `string`, and `index` is decremented by 1.",
        "`reversed_string` stores the reverse of `string`, `index` is -1, `string` remains unchanged."
    ),
]

generic_for_ctx = [
    LoopTriple(
        "`n` is 5, `factorial` is 1",
        parse_stmt("""
for i in range(1, n + 1):
    factorial *= i
    """),
        "`factorial` is updated to its previous value multiplied by `n`",
        "Iteration variable `i` starts at 1 and increments by 1 up to 5. At the end of the loop, the variable `factorial` holds the value of the factorial of 5, which is 120, and `n` remains 5. The iteration variable `i` is 5."
    ),
    LoopTriple(
        "`numbers` is a list of integers, `even_numbers` is an empty list.",
        parse_stmt("""
for num in numbers:
    if num % 2 == 0:
        even_numbers.append(num)
        """),
        "If `num` is even, it is appended to list `even_numbers`.",
        "The iteration variable `num` traverses all integers in `numbers`. If in any iteration, `num` is even number, it appends to `even_numbers`. At the end of the loop, the `even_numbers` list contains all even numbers from `numbers` in their original order, and `numbers` remains unchanged. The iteration variable `num` is the last element of `numbers`."
    ),
    LoopTriple(
        "`n` is an integer.",
        parse_stmt("""
for i in range(2, int(math.sqrt(n)) + 1):
    if n % i == 0:
        return True
        """),
        "If `n` divided by `i` has a remainder of 0, the function returns True.",
        "The iteration variable `i` ranges from 2 to the ceiling of the square root of n, incrementing by 1. If `n` is divisible by `i` in any iteration, indicating `n` is not prime, the function returns True. The integer `n` remains unchanged. If the loop completes without returning, the iteration variable `i` is the ceiling of the square root of `n`."
    ),
]


def complete_while_triple(incomplete_triple: LoopTriple, model, context_triples=generic_while_ctx):
    prompt = VERIFYER_SYSTEM_PROMPT_LOOP
    for ctx in context_triples:
        prompt = prompt + "\n" + format_prompt(ctx) + "\n" + f"Postcondition: **{ctx.postcondition}**"
    prompt = prompt + "\n" + format_prompt(incomplete_triple)
    response = model.query(prompt)
    post = extract_postcondition(response)
    # print("*" * 50)
    # print(incomplete_triple)
    # print(f"LLM post: {post}")
    return post


def complete_for_triple(incomplete_triple: LoopTriple, model, context_triples=generic_for_ctx):
    prompt = VERIFYER_SYSTEM_PROMPT_LOOP
    for ctx in context_triples:
        prompt = prompt + "\n" + format_prompt(ctx) + "\n" + f"Postcondition: **{ctx.postcondition}**"
    prompt = prompt + "\n" + format_prompt(incomplete_triple)
    response = model.query(prompt)
    post = extract_postcondition(response)
    # print("*" * 50)
    # print(incomplete_triple)
    # print(f"LLM post: {post}")
    return post
