import os
from dataclasses import dataclass
import ast
import astor
from ast import AST
from enum import Enum, auto
import json

import openai
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff

MODEL = "gpt-3.5-turbo"

VERIFYER_SYSTEM_PROMPT = """
You are assigned the role of a program verifier, responsible for completing Hoare triples. Each Hoare triple is made up of three components: a precondition, a program fragment, and a postcondition. The precondition and the postcondition are expressed in natural language.

Precondition: describes the initial state of the program variables before the execution of the program fragment. This description should only include the values of the variables, without detailing the operational aspects of the program.

Program Fragment: This is a given part of the task and is not something you need to create or modify.

Postcondition: describes the state of the program variables after the execution of the program fragment with the initial state described in the precondition. This description should include both the values of the variables and the relationships between them. Similar to the precondition, avoid explaining how the program operates; concentrate solely on the variable values and their interrelations.
"""

DEFAULT_TEMPERATURE = 0.7

openai.api_key = os.getenv("OPENAI_API_KEY")


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def completion_with_backoff(**kwargs):
    return openai.ChatCompletion.create(**kwargs)


def parse_stmt(source):
    return ast.parse(source).body[0]


class State(Enum):
    TOP = auto()
    BOTTOM = auto()    
    UNKNOWN = auto()

def print_state(s):
    if s == State.UNKNOWN:
        return "the state is unknown"
    if s == State.TOP:
        return "variables can hold any values"
    if s == State.BOTTOM:
        return "the state is unreachable"
    return s

@dataclass
class Triple:
    precondition: str
    command: AST
    postcondition: str

    def __str__(self):
        return f"{{ {print_state(self.precondition)} }}\n{pprint_cmd(self.command)}{{ {print_state(self.postcondition)} }}"

    def with_postcondition(self, pc):
        return Triple(self.precondition, self.command, pc)


def complete_triple(context_triples, incomplete_triple):
    msgs = []
    msgs.append({"role": "system", "content": VERIFYER_SYSTEM_PROMPT })
    for ctx in context_triples:
        msgs.append({"role": "system", "name": "example_user", "content": format_prompt(ctx)})
    msgs.append({"role": "user", "content": format_prompt(incomplete_triple)})
    response = completion_with_backoff(model=MODEL, messages=msgs, temperature=DEFAULT_TEMPERATURE)
    post = postprocess_completion(response.choices[0].message.content)
    return post

def postprocess_completion(s):
    keyword = "Postcondition:"
    if keyword in s:
        return s.split(keyword, 1)[1].strip()
    return s

def pprint_cmd(cmd):
    if isinstance(cmd, list):
        return "\n".join([astor.to_source(c) for c in cmd])
    else:
        return astor.to_source(cmd)

def format_prompt(triple):
    if triple.postcondition is State.UNKNOWN:
        return f"Precondition: {triple.precondition}\n```\n{pprint_cmd(triple.command)}```\nPostcondition: "
    return f"Precondition: {triple.precondition}\n```\n{pprint_cmd(triple.command)}```\nPostcondition: {triple.postcondition}"


source = """
if n <= 1:
  return n

prev, curr = 0, 1
for _ in range(2, n + 1):
  prev, curr = curr, prev + curr

return curr
"""

generic_ctx = [
    Triple(
        State.TOP,
        parse_stmt("n = int(input())"),
        "n is an input integer"),
    Triple(
        "n is either 3 or 5",
        parse_stmt("m = n + 1"),
        "n is either 3 or 5; m is either 4 or 6"),
    Triple(
        "x is greater than zero",
        parse_stmt("x = x + 1"),
        "x is greater than one")
]

def complete_triple_cot(triple):
    assert triple.postcondition == State.UNKNOWN
    if isinstance(triple.command, ast.Assign) or isinstance(triple.command, ast.Expr) or isinstance(triple.command, ast.Return):
        post = complete_triple(generic_ctx, triple)
        return post
    if isinstance(triple.command, list):
        pre = triple.precondition
        ctx = []
        for subcmd in triple.command:
            completion = complete_triple_cot(Triple(pre, subcmd, State.UNKNOWN))
            ctx.append(Triple(pre, subcmd, completion))
            pre = completion
        return complete_triple(ctx, triple)
    if isinstance(triple.command, ast.If):
        pre = triple.precondition
        then_completion = complete_triple_cot(Triple(pre, triple.command.body, State.UNKNOWN))
        ctx = [Triple(pre, triple.command.body, then_completion)]        
        if triple.command.orelse:
            else_completion = complete_triple_cot(Triple(pre, triple.command.orelse, State.UNKNOWN))
            ctx.append(Triple(pre, triple.command.orelse, else_completion))
        return complete_triple(ctx, triple)
    if isinstance(triple.command, ast.For):
        pre = State.TOP
        body_completion = complete_triple_cot(Triple(pre, triple.command.body, State.UNKNOWN))
        ctx = [Triple(pre, triple.command.body, body_completion)]
        return complete_triple(ctx, triple)
    if isinstance(triple.command, ast.While):
        pre = State.TOP
        body_completion = complete_triple_cot(Triple(pre, triple.command.body, State.UNKNOWN))
        ctx = [Triple(pre, triple.command.body, body_completion)]
        return complete_triple(ctx, triple)
    raise ValueError(f"unsupported statement type: {triple.command} {pprint_cmd(triple.command)}")

cmd = ast.parse(source).body
triple = Triple("n is a positive integer", cmd, State.UNKNOWN)

print(triple)

print("=========== non-CoT: ===========")
post = complete_triple(generic_ctx, triple)
print(post)

print("============= CoT: =============")
post_cot = complete_triple_cot(triple)
print(post_cot)
