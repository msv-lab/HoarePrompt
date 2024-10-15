from dataclasses import dataclass
from enum import Enum, auto
import ast
import astor

# Enum to define different states of the program or variables 
class State(Enum):
    TOP = auto() # Represents the top state where variables can hold any values
    BOTTOM = auto() # Represents an unreachable state 
    UNKNOWN = auto() # Represents an unknown state, this is when we want to find through a model querry the state of the variables
    NEW = auto()  # Represents a newly defined state, this is used for uninitialized variables


def print_state(s: State | str) -> str:
    if s == State.UNKNOWN:
        return "the state is unknown"
    if s == State.TOP:
        return "variables can hold any values"
    if s == State.BOTTOM:
        return "the state is unreachable"
    if s == State.NEW:
        return "variables are newly defined"
    return s

# The base Hoare triple class. It is the standard unit we base the verification on with precondition, command, and postcondition
@dataclass
class Triple:
    precondition: str | State
    command: ast.AST | list  # The command, which is a program fragment, represented as an AST node or a list of nodes
    postcondition: str | State

    # Returns the Hoare triple as a formatted string
    def __str__(self):
        return f"{{ {print_state(self.precondition)} }}\n{pprint_cmd(self.command)}{{ {print_state(self.postcondition)} }}"

    # Adds the postocndition to the triple (obviously after the triple has been computed by the model)
    def with_postcondition(self, pc):
        return Triple(self.precondition, self.command, pc)

# Specialized Hoare triple for 'if' statements, capturing both 'if' and 'else' postconditions
@dataclass
class IfTriple:
    precondition: str | State
    command: ast.AST
    if_postcondition: str
    else_postcondition: str # Can be none if there is no else
    postcondition: str | State

    def __str__(self):
        return f"{{ {print_state(self.precondition)} }}\n{pprint_cmd(self.command)}\nIf Post: {self.if_postcondition}\nElse Post: {'there is no else part in the code' if self.else_postcondition is None else self.else_postcondition}\n{{ {print_state(self.postcondition)} }}"

# Specialized Hoare triple for function definitions. It includes the function body and its signature as well as the postcondition of the body and postcondition of the function
@dataclass
class FuncTriple:
    precondition: str | State
    command: ast.AST
    head: str
    body_command: list # The list of commands inside the function body
    body_postcondition: str # Postcondition of the funtion body
    postcondition: str | State # postcondition after the function returns

    def __str__(self):
        return f"{{ {print_state(self.precondition)} }}\n{self.head}\nBody Post: {self.body_postcondition}\n{{ {print_state(self.postcondition)} }}"

# Specialized Hoare triple for try-except blocks. It includes both try and except parts and their postconditions
@dataclass
class TryTriple:
    precondition: str | State
    command: ast.AST # The try-except block as an AST node
    try_command: list
    try_post: str
    except_command: list
    except_post: str
    postcondition: str | State # Overall postcondition after the entire try-except block


# It converts the given source code string into an AST.
# Then it returns the first statement from the parsed body of the code, as an AST node.
def parse_stmt(source: str) -> ast.AST:
    return ast.parse(source).body[0]

# Function to pretty-print a command, which is either a single AST node or a list of nodes, as source code
def pprint_cmd(cmd: ast.AST | list) -> str:
    if isinstance(cmd, list):
        return "\n".join([astor.to_source(c) for c in cmd])
    else:
        return astor.to_source(cmd)
