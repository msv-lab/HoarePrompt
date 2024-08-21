import sys
import os
import ast
import re
import astor
from dataclasses import dataclass
from enum import Enum, auto
import ast
import astor
import json


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
    command: ast.AST
    postcondition: str

    def __str__(self):
        return f"{{ {print_state(self.precondition)} }}\n{pprint_cmd(self.command)}{{ {print_state(self.postcondition)} }}"

    def with_postcondition(self, pc):
        return Triple(self.precondition, self.command, pc)


def parse_stmt(source):
    return ast.parse(source).body[0]


def pprint_cmd(cmd):
    if isinstance(cmd, list):
        return "\n".join([astor.to_source(c) for c in cmd])
    else:
        return astor.to_source(cmd)


VERIFYER_SYSTEM_PROMPT = """You are assigned the role of a program verifier, responsible for completing Hoare triples. Each Hoare triple is made up of three components: a precondition, a program fragment, and a postcondition. The precondition and the postcondition are expressed in natural language.

Precondition: describes the initial state of the program variables before the execution of the program fragment. This description should only include the values of the variables, without detailing the operational aspects of the program.

Program Fragment: This is a given part of the task and is not something you need to create or modify.

Postcondition: describes the state of the program variables after the execution of the program fragment with the initial state described in the precondition. This description should include both the values of the variables and the relationships between them. Similar to the precondition, avoid explaining how the program operates; concentrate solely on the variable values and their interrelations."""


generic_ctx = [
    Triple(
        "n can be any value",
        parse_stmt("n = int(input())"),
        "n is an input integer",
    ),
    Triple(
        "n is either 3 or 5",
        parse_stmt("m = n + 1"),
        "n is either 3 or 5; m is either 4 or 6",
    ),
    Triple("x is greater than zero", parse_stmt("x = x + 1"), "x greater than one"),
    Triple("n is a bool value", parse_stmt("num = 5"), "n is a bool value, num is 5"),
    Triple(
        "i is integer", parse_stmt("i += 1"), "i is integer and i is increased by 1"
    ),
    Triple(
        State.TOP,
        parse_stmt("raise ValueError('An error occurred')"),
        "ValueError is raised",
    ),
    Triple(
        State.TOP,
        parse_stmt("return True"),
        "the function return True",
    ),
    Triple(
        "n is an integer, m is 2",
        parse_stmt(
            '''if n < m:
    return True
    """the function return True"""'''
        ),
        "n is an integer, m is 2. If n is less then 2, then the function return True",
    ),
]


def complete_triple(model, incomplete_triple, context_triples=generic_ctx):
    prompt = VERIFYER_SYSTEM_PROMPT
    for ctx in context_triples:
        prompt = prompt + "\n" + format_prompt(ctx) + "\n" + f"Postcondition: **{ctx.postcondition}**"
    prompt = prompt + "\n" + format_prompt(incomplete_triple)
    response = model.query(prompt)
    post = extract_postcondition(response)
    return post


def format_prompt(triple: Triple) -> str:
    precondition_comment = f'"""{print_state(triple.precondition)}"""\n'
    program_with_precondition = precondition_comment + pprint_cmd(triple.command)
    return program_with_precondition


def extract_postcondition(s: str) -> str:
    pattern = r"Postcondition:\s*\*\*(.*?)\*\*"
    match = re.search(pattern, s, re.DOTALL)
    if match:
        return match.group(1)
    return s


class Annotator(ast.NodeTransformer):
    def __init__(self):
        self.comments = []

    def add_comment(self, comment, lineno):
        self.comments.append((comment, lineno))
        self.last = (comment, lineno)

    def _insert_comments_into_block(self, block):
        if isinstance(block, list):
            new_block = []
            for child in block:
                new_block.append(self.visit(child))
                for comment, lineno in self.comments[:]:
                    if hasattr(child, "lineno") and child.lineno == lineno:
                        new_comment = ast.Expr(value=ast.Constant(value=f"{comment}"))
                        new_comment.lineno = lineno
                        new_block.append(new_comment)
                        self.comments.remove((comment, lineno))
            return new_block
        return block

    def insert_comments(self, node):
        if hasattr(node, "body"):
            node.body = self._insert_comments_into_block(node.body)
        
        if hasattr(node, "orelse"):
            node.orelse = self._insert_comments_into_block(node.orelse)

        if hasattr(node, "finalbody"):
            node.finalbody = self._insert_comments_into_block(node.finalbody)
        
        if hasattr(node, "handlers"):
            for handler in node.handlers:
                handler.body = self._insert_comments_into_block(handler.body)

        return node

    def visit(self, node):
        return self.insert_comments(super().generic_visit(node))


class Deletor(ast.NodeTransformer):
    def __init__(self):
        self.comments_to_keep = []

    def append_comment_to_keep(self, comment):
        self.comments_to_keep.append(comment)

    def remove_comment_to_keep(self, comment):
        self.comments_to_keep.remove(comment)

    def _remove_comments_from_block(self, block):
        if isinstance(block, list):
            new_block = []
            for child in block:
                if not (
                    isinstance(child, ast.Expr)
                    and isinstance(child.value, ast.Constant)
                    and (child.value.value, child.lineno) not in self.comments_to_keep
                ):
                    new_block.append(self.visit(child))
            return new_block
        return block

    def remove_comments(self, node):
        if hasattr(node, "body"):
            node.body = self._remove_comments_from_block(node.body)
        
        if hasattr(node, "orelse"):
            node.orelse = self._remove_comments_from_block(node.orelse)

        if hasattr(node, "finalbody"):
            node.finalbody = self._remove_comments_from_block(node.finalbody)
        
        if hasattr(node, "handlers"):
            for handler in node.handlers:
                handler.body = self._remove_comments_from_block(handler.body)

        return node

    def visit(self, node):
        return self.remove_comments(super().generic_visit(node))


def print_code(node, message="Current code"):
    code = astor.to_source(node)
    print(f"{message}:\n{code}", file=sys.stderr)


def complete_triple_cot(
        model, triple: Triple, annotator: Annotator, deletor: Deletor, node
) -> tuple:
    assert triple.postcondition == State.UNKNOWN
    if isinstance(
        triple.command,
        (
            ast.Assign,
            ast.AugAssign,
            ast.Expr,
            ast.Return,
            ast.Raise,
            ast.Pass,
            ast.Break,
            ast.Continue,
        ),
    ):
        post = complete_triple(model, triple)
        lineno = triple.command.lineno
        return post, lineno

    elif isinstance(triple.command, list):
        pre = triple.precondition
        temp = []
        for subcmd in triple.command:
            completion, lineno = complete_triple_cot(
                model, Triple(pre, subcmd, State.UNKNOWN), annotator, deletor, node
            )
            annotator.add_comment(completion, lineno)
            annotator.visit(node)
            deletor.append_comment_to_keep((completion, lineno))
            temp.append((completion, lineno))
            print_code(node, "After a element in list")
            pre = completion

        overall_post = complete_triple(model, triple)
        last_lineno = triple.command[-1].lineno if triple.command else 0
        for item in temp:
            deletor.remove_comment_to_keep(item)
        deletor.visit(node)
        return overall_post, last_lineno

    elif isinstance(triple.command, ast.If):
        pre = triple.precondition
        then_completion, then_lineno = complete_triple_cot(
            model, Triple(pre, triple.command.body, State.UNKNOWN), annotator, deletor, node
        )
        ctx = [Triple(pre, triple.command.body, then_completion)]

        if triple.command.orelse:
            else_completion, else_lineno = complete_triple_cot(
                model,
                Triple(pre, triple.command.orelse, State.UNKNOWN),
                annotator,
                deletor,
                node,
            )
            ctx.append(Triple(pre, triple.command.orelse, else_completion))
            last_lineno = max(then_lineno, else_lineno)
        else:
            last_lineno = then_lineno

        overall_post = complete_triple(model, triple, ctx)
        return overall_post, last_lineno

    elif isinstance(triple.command, ast.Try):
        pre = triple.precondition

        try_completion, try_lineno = complete_triple_cot(
            model, Triple(pre, triple.command.body, State.UNKNOWN), annotator, deletor, node
        )

        except_completion, except_lineno = complete_triple_cot(
            model,
            Triple(State.UNKNOWN, triple.command.handlers, State.UNKNOWN),
            annotator,
            deletor,
            node,
        )
        ctx = [Triple(pre, triple.command.body, try_completion), Triple(State.UNKNOWN, triple.command.body, except_completion)]
        if triple.command.orelse:
            else_completion, else_lineno = complete_triple_cot(
                model,
                Triple(try_completion, triple.command.orelse, State.UNKNOWN),
                annotator,
                deletor,
                node,
            )
            ctx.append(Triple(pre, triple.command.orelse, else_completion))
        else:
            else_lineno = try_lineno

        if triple.command.finalbody:
            finally_completion, finally_lineno = complete_triple_cot(
                model,
                Triple(State.UNKNOWN, triple.command.finalbody, State.UNKNOWN),
                annotator,
                deletor,
                node,
            )
            ctx.append(Triple(State.UNKNOWN, triple.command.orelse, finally_completion))
            last_lineno = max(try_lineno, except_lineno, else_lineno, finally_lineno)
        else:
            last_lineno = max(try_lineno, except_lineno, else_lineno)

        overall_post = complete_triple(model,triple, ctx)
        return overall_post, last_lineno

    elif isinstance(triple.command, ast.For):
        pre = triple.precondition
        body_completion, body_lineno = complete_triple_cot(
            model, Triple(pre, triple.command.body, State.UNKNOWN), annotator, deletor, node
        )
        ctx = [Triple(pre, triple.command.body, body_completion)]
        overall_post = complete_triple(model, triple, ctx)

        last_lineno = triple.command.body[-1].lineno if triple.command.body else 0
        return overall_post, last_lineno

    elif isinstance(triple.command, ast.While):
        pre = triple.precondition
        body_completion, body_lineno = complete_triple_cot(
            model, Triple(pre, triple.command.body, State.UNKNOWN), annotator, deletor, node
        )
        ctx = [Triple(pre, triple.command.body, body_completion)]
        overall_post = complete_triple(model, triple, ctx)

        last_lineno = triple.command.body[-1].lineno if triple.command.body else 0
        return overall_post, last_lineno

    elif isinstance(triple.command, ast.FunctionDef):
        pre = triple.precondition
        body_completion, body_lineno = complete_triple_cot(
            model, Triple(pre, triple.command.body, State.UNKNOWN), annotator, deletor, node
        )
        ctx = [Triple(pre, triple.command.body, body_completion)]
        overall_post = complete_triple(model, triple, ctx)
        last_lineno = triple.command.body[-1].lineno if triple.command.body else 0
        return overall_post, last_lineno

    elif isinstance(triple.command, (ast.Import, ast.ImportFrom, ast.Assert)):
        return triple.precondition, 0

    raise ValueError(
        f"unsupported statement type: {triple.command} {pprint_cmd(triple.command)}"
    )


def compute_postcondition(model, precondition, program, config):
    parsed_code = ast.parse(program)
    triple = Triple(precondition, parsed_code.body, State.UNKNOWN)
    annotator = Annotator()
    deletor = Deletor()
    response, line = complete_triple_cot(model, triple, annotator, deletor, parsed_code)
    return response
