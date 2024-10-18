import re

from node_base_style.hoare_triple import Triple, IfTriple, FuncTriple, print_state, pprint_cmd

#This script helps in constructing prompts depending on the AST node type (for example and if triple) and parsing the language model's output to find the postcondition

def format_prompt(triple: Triple | IfTriple | FuncTriple) -> str:
    # This function generates prompts for the LLM based on different AST nodes.
    if isinstance(triple, Triple):
        format_str = f"Precondition: {print_state(triple.precondition)}\nProgram fragment:\n```\n{pprint_cmd(triple.command)}\n```"

    if isinstance(triple, IfTriple):
        format_str = f"Precondition: {print_state(triple.precondition)}\nProgram fragment:\n```\n{pprint_cmd(triple.command)}\n```\nPostcondition for if body: {triple.if_postcondition}\nPostcondition for else body: {'there is no else part in the code' if triple.else_postcondition is None else triple.else_postcondition}"

    if isinstance(triple, FuncTriple):
        format_str = f"Precondition: {print_state(triple.precondition)}\nProgram fragment:\n```\n{pprint_cmd(triple.command)}\n```\nPostcondition for function body: {triple.body_postcondition}"

    return format_str

# Extracts the postcondition from the model's response
import re

def extract_postcondition(s: str) -> str:
    pattern = r"Postcondition:\s*\*\*(.*?)\*\*"
    matches = re.findall(pattern, s, re.DOTALL)
    if matches:
        # Select the last match
        res = matches[-1]
        # Clean up the beginning and end of the string for any weird characters like * or newlines
        return res.strip()
    return s


# Extracts the result from the model's response given a keyword . For example the keyword can be "Output State"
# Same as extact_postcondition if the keyword is "Postcondition"
def extract_result(s: str, keyword: str) -> str:
    pattern = fr"{keyword}:\s*\*\*(.*?)\*\*"
    matches = re.findall(pattern, s, re.DOTALL)
    if matches:
        # Select the last match
        res = matches[-1]
        # Clean up the beginning and end of the string for any weird characters like * or newlines
        return res.strip()
    return s

