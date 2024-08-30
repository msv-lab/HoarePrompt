from node_base_style.hoare_triple import FuncTriple, parse_stmt
from node_base_style.helper import extract_postcondition, format_prompt


VERIFYER_SYSTEM_PROMPT_FUNC = """You are assigned the role of a program verifier, responsible for completing the Hoare triples of Python functions. Each Hoare triple is made up of three components: a precondition, a program fragment, and a postcondition. The precondition and the postcondition are expressed in natural language. In addition to the Hoare triple, you will also see the postcondition of the function body. You need to combine this with the postcondition of the function body to provide the overall postcondition of the function.

Precondition: describes the initial state of the program variables before the execution of the program fragment. This description should only include the values of the variables, without detailing the operational aspects of the program.

Program Fragment: This is a given part of the task and is not something you need to create or modify.

Postcondition: describes the state of the program variables after the execution of the program fragment with the initial state described in the precondition. This description should include both the values of the variables and the relationships between them. Similar to the precondition, avoid explaining how the program operates; concentrate solely on the variable values and their interrelations. You need to strictly follow the format."""

generic_func_ctx = [
    FuncTriple(
        "`number` is an integer.",
        parse_stmt('''
def is_even(number):
    if number % 2 == 0:
        return True
    return False
        '''),
        "`number` is an integer. If `number` is even, the function returns True; otherwise, it returns False.",
        "The function `is_even` takes an integer parameter `number`. If the `number` is even, the function returns `True`; otherwise, it returns `False`."
    ),
    FuncTriple(
        "`celsius` is a float",
        parse_stmt('''
def celsius_to_fahrenheit(celsius):
    return (celsius * 9/5) + 32
        '''),
        "The function returns (`celsius` * 9/5) + 32",
        "The function takes a floating-point parameter `celsius` and, in all cases, returns `(celsius * 9/5) + 32`."
    ),
    FuncTriple(
        "`strings` is a list of string and `char` is a character",
        parse_stmt('''
def find_first_string_with_char(strings, char):
    for s in strings:
        if char in s:
            return s
    return None
        '''),
        "The iteration variable `s` traverses each string in the list `strings`. During any iteration, if the character `char` is found in `s`, the function returns `s`. If no such `s` is found during the loop, then `s` is the last string in the list, the function returns `None`.",
        "The function `find_first_string_with_char` takes two parameters: a list of strings, `strings`, and a character, `char`. The function iterates through each string in `strings`, and if `char` is found in a string, that string is returned and the function terminates. If `char` is not found in any of the strings, the function returns `None` after the loop completes."
    ),
]


def complete_func_triple(incomplete_triple: FuncTriple, model, context_triples=generic_func_ctx):
    prompt = VERIFYER_SYSTEM_PROMPT_FUNC
    for ctx in context_triples:
        prompt = prompt + "\n" + format_prompt(ctx) + "\n" + f"Postcondition: **{ctx.postcondition}**"
    prompt = prompt + "\n" + format_prompt(incomplete_triple)
    response = model.query(prompt)
    post = extract_postcondition(response)
    print("*" * 50)
    print(incomplete_triple)
    print(f"LLM post: {post}")
    return post
