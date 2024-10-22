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
    


def pprint_if_stmt(cmd: ast.AST | list) -> str:
    if isinstance(cmd, list):
        for c in cmd:
            if isinstance(c, ast.If):
                # Return only the condition (test) of the if statement
                if c.test:
                    return astor.to_source(c.test).strip()
        # If no 'If' block is found in the list, return an empty string or some indication
        return "No if condition found"
    else:

        return "if " + astor.to_source(cmd.test).strip() +" :"

            
def pprint_else_stmt(cmd: ast.AST | list) -> str:
    if isinstance(cmd, list):
        for c in cmd:
            
            if isinstance(c, ast.If):
                # Return the elif condition
                return f"elif {astor.to_source(c.test).strip()}:"
            else:
                # If it's not an elif, return else
                return "else:"
        # If no elif or else block is found, return an empty string or some indication
        return "No elif or else block found"
    else:
        return "else :"
    
def pprint_try_stmt(cmd: ast.AST | list) -> str:
    if isinstance(cmd, list):
        for c in cmd:
            if isinstance(c, ast.Try):
                return "try:"
        return "No try block found"
    else:
        return "try:"
    
def pprint_except_stmt(cmd: ast.AST | list) -> str:
    if isinstance(cmd, list):
        for c in cmd:
            if isinstance(c, ast.ExceptHandler):
                # If there is an exception type, get its source code; otherwise, return a generic "except:"
                if c.type:
                    return f"except ({astor.to_source(c.type).strip()}):"
                else:
                    return "except:"
        return "No except block found"
    else:
        if isinstance(cmd, ast.ExceptHandler):
            if cmd.type:
                return f"except ({astor.to_source(cmd.type).strip()}):"
            else:
                return "except:"
        else:
            return "No except block found"
       