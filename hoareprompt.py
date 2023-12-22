import os
from dataclasses import dataclass
import ast
import astor
from ast import AST
from enum import Enum, auto

import openai
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff

MODEL = "gpt-3.5-turbo"

VERIFYER_SYSTEM_PROMPT = """
You are a program verifyer that completes Hoare triples. Each triple consists of a precondition written in natural language, a program fragment, and a postcondition written in natural language. The precondition describes the initial state, that is the values of program varibles before the fragment is executed. The postcondition describe the values of program variables as well as the relationship between them after the fragment is executed. In precondition and postcondition, do not describe how the program operates. Only describe the values of program variables and their relationship.
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


@dataclass
class Triple:
    precondition: str
    command: AST
    postcondition: str

    def __str__(self):
        return f"{{ {self.precondition} }}\n{pprint_cmd(self.command)}{{ {self.postcondition} }}"

    def with_postcondition(self, pc):
        return Triple(self.precondition, self.command, pc)


def complete_triple(context_triples, incomplete_triple):
    msgs = []
    msgs.append({"role": "system", "content": VERIFYER_SYSTEM_PROMPT })
    for ctx in context_triples:
        msgs.append({"role": "system", "name": "example_user", "content": format_prompt(ctx)})
    msgs.append({"role": "user", "content": format_prompt(incomplete_triple)})
    response = completion_with_backoff(model=MODEL, messages=msgs, temperature=DEFAULT_TEMPERATURE)
    return postprocess_completion(response.choices[0].message.content)

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
n = int(input())
a = list(map(int, input().split()))

max_a = max(a)
min_d = float('inf')

for D in range(max_a + 1):
    max_ai = float('-inf')
    min_ai = float('inf')
    
    for ai in a:
        max_ai = max(max_ai, ai + D)
        min_ai = min(min_ai, ai - D)
    
    if (max_ai - min_ai) % (2 * D) == 0:
        min_d = min(min_d, D)

if min_d == float('inf'):
    print(-1)
else:
    print(min_d)
"""

generic_ctx = [
    Triple(
        "Unknown state",
        parse_stmt("z = 1"),
        "z is 1"),
    Triple(
        "Unknown state",
        parse_stmt("n = int(input())"),
        "n is an input integer"),
    Triple(
        "n is either 3 or 5",
        parse_stmt("m = n + 1"),
        "n is either 3 or 5; m is either 4 or 6"),
    Triple(
        "x is greater than zero",
        parse_stmt("x = x + 1"),
        "x is greater than one"),
    Triple(
        "Any",
        parse_stmt("x = input()"),
        "x is a program input"),
]

def complete_triple_cot(triple):
    assert triple.postcondition == State.UNKNOWN
    if isinstance(triple.command, ast.Assign) or isinstance(triple.command, ast.Expr):
        post = complete_triple(generic_ctx, triple)
        return triple.with_postcondition(post)
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
        pre = State.UNKNOWN
        body_completion = complete_triple_cot(Triple(pre, triple.command.body, State.UNKNOWN))
        ctx = [Triple(pre, triple.command.body, body_completion)]
        return complete_triple(ctx, triple)
    if isinstance(triple.command, ast.While):
        pre = State.UNKNOWN
        body_completion = complete_triple_cot(Triple(pre, triple.command.body, State.UNKNOWN))
        ctx = [Triple(pre, triple.command.body, body_completion)]
        return complete_triple(ctx, triple)
    raise ValueError(f"unsupported statement type: {triple.command} {pprint_cmd(triple.command)}")

cmd = ast.parse(source).body
triple = Triple(State.UNKNOWN, cmd, State.UNKNOWN)

print(triple)

print("=========== non-CoT: ===========")
post = complete_triple(generic_ctx, triple)
print(post)

print("============= CoT: =============")
post_cot = complete_triple_cot(triple)
print(post_cot)


