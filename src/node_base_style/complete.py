import ast

from node_base_style.hoare_triple import State, Triple, IfTriple, FuncTriple, TryTriple, pprint_cmd
from node_base_style.general import complete_triple
from node_base_style.if_statement import complete_if_triple
from node_base_style.function_definition import complete_func_triple, get_func_def
from node_base_style.loop import complete_loop_triple, get_while_head, ForToWhileTransformer
from node_base_style.loop_condition import get_precondition
from node_base_style.try_statement import complete_try_triple


# This is a class responsible for analyzing the postcondition of a program given its precondition and source code
class PostconditionAnalyzer:
    def __init__(self, model, config):
        self.model = model
        self.config = config
        self.collected_returns = []  # Collects postconditions from return statements as strings
        self.got_return = False # Flag to check if a return statement was encountered in the same level of recursion
        self.last_return =""
    # Core recursive method to compute the postcondition of a Triple .
    def complete_triple_cot(self, triple: Triple, depth=0) -> str:
        assert triple.postcondition == State.UNKNOWN

        #generic easy case
        if isinstance(triple.command,
                      (ast.Assign, ast.AugAssign, ast.Expr, ast.Raise, ast.Pass, ast.Break, ast.Continue)):
            post = complete_triple(triple, self.model)
            return post

        # Handle return statements
        if isinstance(triple.command, ast.Return):
            post = complete_triple(triple, self.model)
            # If we're at the first level of depth (inside a function), collect the return postcondition and we are done for this recursion
            if depth == 1 :
                self.got_return = True
                self.last_return = str(post)
                #self.collected_returns.append(str(post))
            return post

        # case where there are multiple statements, like a function body or a block of code
        if isinstance(triple.command, list):
            pre = triple.precondition
            # Recursively compute the postcondition for each sub-command
            for subcmd in triple.command:
                completion = self.complete_triple_cot(Triple(pre, subcmd, State.UNKNOWN), depth=depth)
                pre = completion
                if self.got_return:
                    break
            return pre
        
        # Case for if statements
        if isinstance(triple.command, ast.If):
            pre = triple.precondition
            # Find the postcondition for the if body
            then_completion = self.complete_triple_cot(Triple(pre, triple.command.body, State.UNKNOWN), depth=depth)
            if_post = then_completion

            else_post = None
            if triple.command.orelse:
                # If there is an else part, find the postcondition for it
                else_completion = self.complete_triple_cot(Triple(pre, triple.command.orelse, State.UNKNOWN),
                                                           depth=depth)
                else_post = else_completion

            # Create an IfTriple to represent the if statement with its branches and then compute the overall post condition
            if_triple = IfTriple(pre, triple.command, if_post, else_post, State.UNKNOWN)
            post = complete_if_triple(if_triple, self.model)
            # If we are inside a function and there's a return statement, collect the postcondition and we are done for this recursion
            if depth == 1 and any(isinstance(node, ast.Return) for node in ast.walk(triple.command)):
                self.got_return = False
                print("got return at if")
                self.collected_returns.append(str(post))
                # since the post condition has been appended as a return element we dont deal with it any more
                return pre
            return post

        # Case for try except blocks
        if isinstance(triple.command, ast.Try):
            pre = triple.precondition
            try_command = triple.command.body # Commands inside the try block
            except_command = triple.command.handlers[0].body # Commands inside the first except block
            # First get the postcondition for the try block
            try_completion = self.complete_triple_cot(Triple(pre, try_command, State.UNKNOWN), depth=depth)
            # Then get the postcondition for the except block
            except_completion = self.complete_triple_cot(Triple(State.UNKNOWN, except_command, State.UNKNOWN),
                                                         depth=depth)
            # Create a TryTriple to represent the try-except block and then compute the overall postcondition
            try_triple = TryTriple(pre, triple.command, try_command, try_completion, except_command, except_completion,
                                   State.UNKNOWN)

            post = complete_try_triple(try_triple, self.model)
            # If we are inside a function and there's a return statement, collect the postcondition and we are done for this recursion
            if depth == 1 and any(isinstance(node, ast.Return) for node in ast.walk(triple.command)):
                self.collected_returns.append(str(post))
                self.got_return = False
                 # since the post condition has been appended as a return element we dont deal with it any more
                return pre
            return post
        # This is a tricky case. If the command is a for loop, we need to convert it to a while loop and then compute the postcondition
        if isinstance(triple.command, ast.For):
            t = ForToWhileTransformer()
            while_code = t.visit(triple.command)
            new_triple = Triple(triple.precondition, while_code, State.UNKNOWN)
            return self.complete_triple_cot(new_triple, depth=depth)

        # Case for while loops
        if isinstance(triple.command, ast.While):
            k = self.config["loop-unrolling-count"] # the unrolling param from the config
            body_command = triple.command.body
            while_head = get_while_head(triple.command)
            examples = []
            pre = triple.precondition
            # Unroll the loop by simulating 'k' iterations
            for _ in range(k):
                post = self.complete_triple_cot(Triple(pre, body_command, State.UNKNOWN), depth=depth)
                examples.append(Triple(pre, body_command, post))
                pre = get_precondition(self.model, post, while_head)
            # Create a Triple for the entire 'while' loop
            triple = Triple(triple.precondition, triple.command, State.UNKNOWN)
            post = complete_loop_triple(triple, self.model, examples)
            if depth == 1 and any(isinstance(node, ast.Return) for node in ast.walk(triple.command)):
                self.collected_returns.append(post)
                self.got_return = False
                 # since the post condition has been appended as a return element we dont deal with it any more
                return pre

            return post

        # Case for function definitions
        if isinstance(triple.command, ast.FunctionDef):
            pre = triple.precondition
            def_str = get_func_def(triple.command) # Get the function signature (the name plus input params of the func) as a string
            
            #this is where the main job is being done by iterating over the body of the function
            self.complete_triple_cot(Triple(pre, triple.command.body, State.UNKNOWN), depth=1)

            #if the got_return flag is True then the last_return ahs not been appended to the collected_returns
            if self.got_return:
                print("got return")
                self.collected_returns.append(self.last_return)
                self.got_return = False
            if len(self.collected_returns) > 1:
                # add Case_{counter} to ecah return postcondition and new line at the end of it
                self.collected_returns= [f"Case_{i+1}: {ret}" for i, ret in enumerate(self.collected_returns)]
            return_conditions_str = "\n".join(self.collected_returns)
            print("return_conditions_str", return_conditions_str)
            #print the self.collected_returns with /n as a separator
            #print("@@@@@@@@@@\n".join(self.collected_returns))

            func_triple = FuncTriple(triple.precondition, triple.command, def_str, triple.command.body,
                                    return_conditions_str, State.UNKNOWN)
            #this gives us the functionality of the function
            return complete_func_triple(func_triple, self.model)
         
        # Handle import statements and assertions as they dont change the state
        if isinstance(triple.command, (ast.Import, ast.ImportFrom, ast.Assert)):
            return triple.precondition

        raise ValueError(f"unsupported statement type: {triple.command} {pprint_cmd(triple.command)}")

# Function to compute the postcondition of a whole program
# This is the function that does the heavy lifting
def compute_postcondition(model, precondition, program, config):
    analyzer = PostconditionAnalyzer(model, config)
    parsed_code = ast.parse(program).body
    triple = Triple(precondition, parsed_code, State.UNKNOWN)
    postcondition = analyzer.complete_triple_cot(triple)
    return postcondition
