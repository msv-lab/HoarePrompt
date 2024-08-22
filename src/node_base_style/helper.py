import re

from node_base_style.hoare_triple import Triple, IfTriple, LoopTriple, FuncTriple, print_state, pprint_cmd


def format_prompt(triple: Triple | IfTriple | LoopTriple | FuncTriple) -> str:
    # This function generates prompts for the LLM based on different AST nodes.
    if isinstance(triple, Triple):
        return f"Precondition: {print_state(triple.precondition)}\nProgram fragment:\n```\n{pprint_cmd(triple.command)}\n```"

    if isinstance(triple, IfTriple):
        return f"Precondition: {print_state(triple.precondition)}\nProgram fragment:\n```\n{pprint_cmd(triple.command)}\n```\nPostcondition for if body: {triple.if_postcondition}\nPostcondition for else body: {'there is no else part in the code' if triple.else_postcondition is None else triple.else_postcondition}"

    if isinstance(triple, LoopTriple):
        return f"Precondition: {print_state(triple.precondition)}\nProgram fragment:\n```\n{pprint_cmd(triple.command)}\n```\nPostcondition for loop body: {triple.body_postcondition}"

    if isinstance(triple, FuncTriple):
        return f"Precondition: {print_state(triple.precondition)}\nProgram fragment:\n```\n{pprint_cmd(triple.command)}\n```\nPostcondition for function body: {triple.body_postcondition}"


def extract_postcondition(s: str) -> str:
    pattern = r"Postcondition:\s*\*\*(.*?)\*\*"
    match = re.search(pattern, s, re.DOTALL)
    if match:
        return match.group(1)
    return s
