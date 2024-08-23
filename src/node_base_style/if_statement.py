from node_base_style.hoare_triple import IfTriple, parse_stmt, State
from node_base_style.helper import extract_postcondition, format_prompt

VERIFYER_SYSTEM_PROMPT_IF = """You are assigned the role of a program verifier, responsible for completing the overall postcondition of Hoare triples for if statements based on the conditions in the program fragment. In addition to the Hoare triples, you will also see the postconditions for the if and else parts, and if there is an elif part, it will be described in the else postcondition. Each Hoare triple is made up of three components: a precondition, a program fragment, and a postcondition. The precondition and the postcondition are expressed in natural language.

Precondition: describes the initial state of the program variables before the execution of the program fragment. This description should only include the values of the variables, without detailing the operational aspects of the program.

Program Fragment: This is a given part of the task and is not something you need to create or modify. If the program fragment contains nested if statements, you only need to focus on the outermost condition, as the postconditions for the nested if statements are included in the if postcondition and else postcondition.

Postcondition: describes the state of the program variables after the execution of the program fragment with the initial state described in the precondition. This description should include both the values of the variables and the relationships between them. Similar to the precondition, avoid explaining how the program operates; concentrate solely on the variable values and their interrelations. Ensure that the postcondition retains the conditions stated in the precondition. You need to strictly follow the format and summarize the if statement in a coherent paragraph, rather than discussing it in separate paragraphs."""

generic_if_ctx = [
    IfTriple(
        "`str` is a string",
        parse_stmt('''
if len(str) < 3:
    return None
    '''),
        "the function returns None",
        "there is no else part in the code",
        "`str` is a string, if the length of `str` is less then 3, the function return None"
    ),
    IfTriple(
        State.TOP,
        parse_stmt('''
if isinstance(n, int):
    return n
else:
    return int(n)
    '''),
        "The function returns `n`",
        "The function returns `int(n)`",
        "if `n` is integer, then the function returns `n` itself. Otherwise, the function return `int(n)`"
    ),
    IfTriple(
        "`x` is an positive integer",
        parse_stmt('''
if x < 2:
    return False
else:
    return True
    '''),
        "The function return False",
        "The function return True",
        "x is a positive integer, if x is less then 2, the function return False. Otherwise, the function return True"
    ),
    IfTriple(
        "`m` is integer, `n` is an integer",
        parse_stmt('''
if n < 0:
    n = -n
    m += 1
elif n == 0:
    return m
else:
    n -= 13
    m += 1
    '''),
        "the integer `n` is updated to its negation. Integer `m` is increased by 1",
        "If integer `n` is 0, the function returns 0. Otherwise, `n` has been decreased by 13 and integer `m` is increased by 1.",
        "`m`, `n` are integers. If n < 0, `m` is increased by 1 and `n` is negated. If n == 0, the function returns `m`. Otherwise, `n` is decreased by 13 and `m` is increased by 1."
    ),
    IfTriple(
        "x is an integer, y is zero.",
        parse_stmt('''
if x > 0:
    if x > 10:
        y = x * 2
    else:
        y = x + 5
        '''),
        "`x` is an integer. If `x` > 10, `y` is set to twice the value of `x`. Otherwise, `y` is set to the value of `x` plus 5.",
        "there is no else part in the code",
        "`x` is an integer. If `x` is greater than 0 and `x` is greater than 10, then `y` is set to twice the value of x. If `x` is greater than 0 but less than or equal to 10, then `y` is set to the value of x plus 5."
    ),
]


def complete_if_triple(incomplete_triple: IfTriple, model, context_triples=generic_if_ctx):
    prompt = VERIFYER_SYSTEM_PROMPT_IF
    for ctx in context_triples:
        prompt = prompt + "\n" + format_prompt(ctx) + "\n" + f"Postcondition: **{ctx.postcondition}**"
    prompt = prompt + "\n" + format_prompt(incomplete_triple)
    response = model.query(prompt)
    post = extract_postcondition(response)
    # print("*" * 50)
    # print(incomplete_triple)
    # print(f"LLM post: {post}")
    return post
