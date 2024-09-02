from dataclasses import dataclass
from enum import Enum, auto
import ast
import astor


class State(Enum):
    TOP = auto()
    BOTTOM = auto()
    UNKNOWN = auto()
    NEW = auto()


def print_state(s: State | str) -> str:
    if s == State.UNKNOWN:
        return "the state is unknown"
    if s == State.TOP:
        return "variables can hold any values"
    if s == State.BOTTOM:
        return "the state is unreachable"
    return s


@dataclass
class Triple:
    precondition: str | State
    command: ast.AST | list
    postcondition: str | State

    def __str__(self):
        return f"{{ {print_state(self.precondition)} }}\n{pprint_cmd(self.command)}{{ {print_state(self.postcondition)} }}"

    def with_postcondition(self, pc):
        return Triple(self.precondition, self.command, pc)


@dataclass
class IfTriple:
    precondition: str | State
    command: ast.AST
    if_postcondition: str
    else_postcondition: str
    postcondition: str | State

    def __str__(self):
        return f"{{ {print_state(self.precondition)} }}\n{pprint_cmd(self.command)}\nIf Post: {self.if_postcondition}\nElse Post: {'there is no else part in the code' if self.else_postcondition is None else self.else_postcondition}\n{{ {print_state(self.postcondition)} }}"


@dataclass
class FuncTriple:
    precondition: str | State
    command: ast.AST
    head: str
    body_command: list
    body_postcondition: str
    postcondition: str | State

    def __str__(self):
        return f"{{ {print_state(self.precondition)} }}\n{pprint_cmd(self.command)}\nBody Post: {self.body_postcondition}\n{{ {print_state(self.postcondition)} }}"


def parse_stmt(source: str) -> ast.AST:
    return ast.parse(source).body[0]


def pprint_cmd(cmd: ast.AST | list) -> str:
    if isinstance(cmd, list):
        return "\n".join([astor.to_source(c) for c in cmd])
    else:
        return astor.to_source(cmd)
