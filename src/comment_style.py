import sys
import os
import ast # Abstract Syntax Tree for python
import re
import astor # For converting AST back to Python
from dataclasses import dataclass
from enum import Enum, auto # For defining states as enumerations 
import ast
import astor
import json

# The main purpose here is to complete missing postconditions in Hoare triples, based on given preconditions and program fragments.
# Also there are mechanisms to insert and remove comments in the source code to help with debugging or verification.

# Enum to define different states of variables in the Hoare triple
class State(Enum):
    TOP = auto() # Variables can hold any values
    BOTTOM = auto() # Unreachable state
    UNKNOWN = auto() # The postcondition is unknown and needs to be determined by the model


# Function to print the state in human-readable form
def print_state(s):
    if s == State.UNKNOWN:
        return "the state is unknown"
    if s == State.TOP:
        return "variables can hold any values"
    if s == State.BOTTOM:
        return "the state is unreachable"
    return s

# The triple dataclass is a dataclass representing a Hoare triple with precondition, program fragment (command), and postcondition
@dataclass
class Triple:
    precondition: str # The state of the program before execution
    command: ast.AST  # The program fragment in AST form
    postcondition: str # The state of the program after execution

    # Function to print the triple in a human readable format
    def __str__(self):
        return f"{{ {print_state(self.precondition)} }}\n{pprint_cmd(self.command)}{{ {print_state(self.postcondition)} }}"

    # Method to create a new Triple with an updated postcondition, this is for when the model finds it
    def with_postcondition(self, pc):
        return Triple(self.precondition, self.command, pc)

# Parse a statement, which is a single line of code, into an AST node
def parse_stmt(source):
    return ast.parse(source).body[0]

# Pretty-print the command as source code from its AST
def pprint_cmd(cmd):
    if isinstance(cmd, list):
        return "\n".join([astor.to_source(c) for c in cmd])
    else:
        return astor.to_source(cmd)

# Template Hoare triples verification prompt
VERIFYER_SYSTEM_PROMPT = """You are assigned the role of a program verifier, responsible for completing Hoare triples. Each Hoare triple is made up of three components: a precondition, a program fragment, and a postcondition. The precondition and the postcondition are expressed in natural language.

Precondition: describes the initial state of the program variables before the execution of the program fragment. This description should only include the values of the variables, without detailing the operational aspects of the program.

Program Fragment: This is a given part of the task and is not something you need to create or modify.

Postcondition: describes the state of the program variables after the execution of the program fragment with the initial state described in the precondition. This description should include both the values of the variables and the relationships between them. Similar to the precondition, avoid explaining how the program operates; concentrate solely on the variable values and their interrelations."""

# A set of predefined context triples used as few shot examples for model queries
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

# Function to complete a triple by generating a postcondition using the model
def complete_triple(model, incomplete_triple, context_triples=generic_ctx):
    prompt = VERIFYER_SYSTEM_PROMPT
    # Add the few shot examples to the prompt
    for ctx in context_triples:
        prompt = prompt + "\n" + format_prompt(ctx) + "\n" + f"Postcondition: **{ctx.postcondition}**"
    # Add the incomplete triple, without the postcondition to the prompt
    prompt = prompt + "\n" + format_prompt(incomplete_triple)
    # Query the model and extract the postcondition
    response = model.query(prompt)
    post = extract_postcondition(response)
    return post

# Helper function to format a triple into a prompt string
def format_prompt(triple: Triple) -> str:
    precondition_comment = f'"""{print_state(triple.precondition)}"""\n'
    program_with_precondition = precondition_comment + pprint_cmd(triple.command)
    return program_with_precondition

# Function to extract the postcondition from the model's response using regex based on the template format we told the model to print
def extract_postcondition(s: str) -> str:
    pattern = r"Postcondition:\s*\*\*(.*?)\*\*"
    match = re.search(pattern, s, re.DOTALL)
    if match:
        return match.group(1)
    return s

# This is the class responsible for inserting comments into AST nodes
class Annotator(ast.NodeTransformer):
    def __init__(self):
        self.comments = [] # list where the comments are stored

    # Method to add a comment to the list with its corresponding line number
    def add_comment(self, comment, lineno):
        self.comments.append((comment, lineno))
        self.last = (comment, lineno)

    # Insert comments into a block of AST nodes
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
    
    # Insert comments into various parts of an AST node 
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
        # Call the parent class's `generic_visit` method to visit all child nodes of the current AST node
        # Then, insert comments at the appropriate places in the current node
        return self.insert_comments(super().generic_visit(node))

# This is a class responsible for removing comments from AST nodes
class Deletor(ast.NodeTransformer):
    def __init__(self):
        self.comments_to_keep = [] # List with comments to keep

    # Method to add a comment to the list of comments to keep
    def append_comment_to_keep(self, comment):
        self.comments_to_keep.append(comment)

    # Method to remove a comment from the list of comments to keep
    def remove_comment_to_keep(self, comment):
        self.comments_to_keep.remove(comment)

    # Remove comments from a block of AST nodes unless they are marked to be kept
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

    # Remove comments from various parts of an AST node
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

# Helper function to print the current state of the AST node as source code
def print_code(node, message="Current code"):
    code = astor.to_source(node)
    print(f"{message}:\n{code}", file=sys.stderr)

# Recursive function to handle completing triples for different AST node types
def complete_triple_cot(
        model, triple: Triple, annotator: Annotator, deletor: Deletor, node
) -> tuple:
    assert triple.postcondition == State.UNKNOWN # Make sure the state is unknown before completing it
    # Handle various types of AST nodes and recursively complete them
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
    #for the case when the command is a list of statements so multiple commands that each need to be taken into account individually for their effect to the post condition
    elif isinstance(triple.command, list):
        pre = triple.precondition
        temp = []
         # Iterate over each command (subcmd) in the list
        for subcmd in triple.command:
        # Recursively compute the postcondition for each command in the list
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

    # Handling if, try, for, while, function, etc. statements (similar structure, logic)
    # Each is broken down recursively

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

# Main function to compute the postcondition by breaking down the program and recursively completing the post condition for the next Hoare Triplet until the end
def compute_postcondition(model, precondition, program, config):
    parsed_code = ast.parse(program)
    triple = Triple(precondition, parsed_code.body, State.UNKNOWN)
    annotator = Annotator()
    deletor = Deletor()
    response, line = complete_triple_cot(model, triple, annotator, deletor, parsed_code)
    return response
