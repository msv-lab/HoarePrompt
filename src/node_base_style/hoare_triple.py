from dataclasses import dataclass
from enum import Enum, auto
import ast
import astor
from typing import Union

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
    
def pprint_outer_if_else(node: ast.If) -> str:
    """
    Pretty-print only the outermost 'if' condition and 'else:' if it exists.
    """
    if not isinstance(node, ast.If):
        raise ValueError("Input must be an 'ast.If' node.")
    
    result = f"if {ast.unparse(node.test)}:\n"
    if node.orelse:
        result += "else:\n"
    return result

def pprint_if_else(cmd: Union[ast.AST, list]) -> str:
    """
    Recursively pretty-print an AST if-else statement as a string,
    handling nested if-else (including elif cases).
    """
    def helper(node, indent=0):
        spaces = " " * indent
        result = ""
        if isinstance(node, ast.If):
            # Append the 'if' condition
            result += f"{spaces}if {ast.unparse(node.test)}:\n"
            # Append the 'if' body
            for stmt in node.body:
                result += f"{spaces}    {ast.unparse(stmt)}\n"
            # Handle 'else' part
            if node.orelse:
                result += f"{spaces}else:\n"
                for stmt in node.orelse:
                    # Recursively process nested 'if' in 'else'
                    if isinstance(stmt, ast.If):
                        result += helper(stmt, indent + 4)
                    else:
                        result += f"{spaces}    {ast.unparse(stmt)}\n"
        return result

    if isinstance(cmd, list):
        # Process a list of AST nodes
        return "".join(helper(stmt) for stmt in cmd if isinstance(stmt, ast.If))
    elif isinstance(cmd, ast.If):
        # Process a single AST if-node
        return helper(cmd)
    else:
        raise ValueError("Input must be an ast.If node or a list of ast.If nodes.")


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


def pprint_ast_node(node):
    """
    Pretty-print an AST node in its original Python code format.
    """
    if isinstance(node, list):
        # If it's a list of AST nodes, join them with newlines
        return "\n".join(ast.unparse(stmt).strip() for stmt in node)
    elif isinstance(node, ast.AST):
        # If it's a single AST node, unparse it
        return ast.unparse(node).strip()
    else:
        raise ValueError("Input must be an ast.AST node or a list of ast.AST nodes.")
    
def pprint_else_stmt2(node):
    """
    Pretty-print the 'else' or 'elif' part of an if-else AST node, including proper formatting.
    """
    if not isinstance(node, ast.If):
        raise ValueError("Input must be an ast.If node")

    # Handle the `orelse` part
    if node.orelse:
        # Check if the `orelse` starts with another `If` node (elif case)
        first_orelse = node.orelse[0]
        if isinstance(first_orelse, ast.If):
            # Handle `elif` case
            condition = ast.unparse(first_orelse.test).strip()  # Get the condition of the elif
            body = "\n".join("    " + line for line in ast.unparse(first_orelse.body).strip().splitlines())
            # Recursive call to handle the next part of the elif chain
            remaining = pprint_else_stmt(first_orelse)
            return f"elif {condition}:\n{body}\n{remaining}"
        else:
            # Handle `else` case
            body = "\n".join("    " + line for line in ast.unparse(node.orelse).strip().splitlines())
            return f"else:\n{body}"
    else:
        # If there is no `orelse`, return an empty string
        return ""
    
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
       