import ast

from node_base_style.hoare_triple import State, Triple, IfTriple, FuncTriple, TryTriple, pprint_cmd, pprint_else_stmt, pprint_if_stmt, pprint_try_stmt, pprint_except_stmt
from node_base_style.general import complete_triple
from node_base_style.if_statement import complete_if_triple
from node_base_style.function_definition import complete_func_triple, get_func_def
from node_base_style.loop import complete_loop_triple, get_while_head, ForToWhileTransformer
from node_base_style.loop_condition import get_precondition
from node_base_style.try_statement import complete_try_triple
from node_base_style.task_sorter import sort_tasks_by_depth, pretty_print_tasks
from node_base_style.merger import merge_triple
from node_base_style.tree import summarize_functionality_tree


# This is a class responsible for analyzing the postcondition of a program given its precondition and source code
class PostconditionAnalyzer:
    def __init__(self, model, config):
        self.model = model
        self.config = config
        # Collects postconditions from return statements as strings. but i also want it to collect the depth for each postcondition so a list of tuples
        self.collected_returns = []
        self.collected=[]
        self.got_return = False # Flag to check if a return statement was encountered in the same level of recursion
        self.last_return =""
        self.last_return_depth=0
        #create a stack to store the current index
        self.index_stack=[]
        
    # Core recursive method to compute the postcondition of a Triple .
    def complete_triple_cot(self, triple: Triple, depth=0, type ="") -> str:
        assert triple.postcondition == State.UNKNOWN

        #generic easy case
        if isinstance(triple.command,
                      (ast.Assign, ast.AugAssign, ast.Expr, ast.Raise, ast.Pass, ast.Break, ast.Continue)):
            post = complete_triple(triple, self.model)
            if type != "":
                self.collected.append((str(post), depth, f"simple command in {type}", pprint_cmd(triple.command), False))
            else:
                self.collected.append((str(post), depth, "simple command", pprint_cmd(triple.command), False))
            return post

        # Handle return statements
        if isinstance(triple.command, ast.Return):
            post = complete_triple(triple, self.model)
            # If we're at the first level of depth (inside a function), collect the return postcondition and we are done for this recursion
            if depth >= 1 :
                self.got_return = True
                self.last_return = str(post)
                self.last_return_depth= depth
                if type != "":
                    self.collected.append((str(post), depth, f"return statement in {type}", pprint_cmd(triple.command),False))
                else:
                    self.collected.append((str(post), depth, "return statement", pprint_cmd(triple.command), False))
                return post
                #self.collected_returns.append(str(post))
            return post

        # case where there are multiple statements, like a function body or a block of code
        if isinstance(triple.command, list):
            pre = triple.precondition
            # Recursively compute the postcondition for each sub-command
            for subcmd in triple.command:
                completion = self.complete_triple_cot(Triple(pre, subcmd, State.UNKNOWN), depth=depth, type=type)
                pre = completion
                #self.collected.append((str(completion), depth))
                if self.got_return:
                    break
            return pre
        
        # Case for if statements
        if isinstance(triple.command, ast.If):
            pre = triple.precondition

            #push the current index of the  self.collected list in the current stack
            self.index_stack.append(len(self.collected))
            
            # Find the postcondition for the if body
            then_completion = self.complete_triple_cot(Triple(pre, triple.command.body, State.UNKNOWN), depth=depth+1, type="if part")
            if_post = then_completion
            self.collected.append((str(if_post), depth, "the if part of the statement", pprint_if_stmt(triple.command), True))
            
            #if we are inside an if statement and there's a return statement, collect the postcondition and we are done for this recursion
            # if depth >= 1 and any(isinstance(node, ast.Return) for node in ast.walk(triple.command)) and self.got_return:
            #     self.got_return = False
            #     self.collected_returns.append((str(if_post),self.last_return_depth))
            #     self.last_return_depth=0


            else_post = None
            if triple.command.orelse:
                # If there is an else part, find the postcondition for it
                else_completion = self.complete_triple_cot(Triple(pre, triple.command.orelse, State.UNKNOWN),
                                                           depth=depth+1, type="else part")
                else_post = else_completion
                self.collected.append((str(else_post), depth, "the else statement of the if-else block", pprint_else_stmt(triple.command), True))
                # If we are inside a else  and there's a return statement, collect the postcondition and we are done for this recursion
                # if depth >= 1 and any(isinstance(node, ast.Return) for node in ast.walk(triple.command)) and self.got_return:
                #     self.got_return = False
                #     self.collected_returns.append((str(else_post),self.last_return_depth))
                #     self.last_return_depth=0
            # Create an IfTriple to represent the if statement with its branches and then compute the overall post condition
            if_triple = IfTriple(pre, triple.command, if_post, else_post, State.UNKNOWN)
            post = complete_if_triple(if_triple, self.model)
            #if this was an if -else statement keep the postcondition for the total if -else otherwise we insert it with type if-statement
            
            #if we wanna merge the output state of the if-else statement , currently not used
            # merged_output = merge_triple(Triple(post, triple.command, State.UNKNOWN), self.model)
            # post =merged_output
            
            #pop the current index from the stack
            current_index = self.index_stack.pop()
            if triple.command.orelse:
                self.collected.insert(current_index,(str(post), depth, "a summary of the whole if-else block", "", False))
            else:
                self.collected.insert(current_index,(str(post), depth, "a summary of the  whole if block", "", False))
            
           
            # If we are inside a function and there's a return statement, collect the postcondition and we are done for this recursion
            if depth == 1 and any(isinstance(node, ast.Return) for node in ast.walk(triple.command)) and self.got_return:
                self.got_return = False
                self.collected_returns.append((str(post),self.last_return_depth))
                self.last_return_depth=0
                # since the post condition has been appended as a return element we dont deal with it any more
                return pre
            return post

        # Case for try except blocks
        if isinstance(triple.command, ast.Try):
            #push the current index of the  self.collected list in the stack
            self.index_stack.append(len(self.collected))
           
            
            pre = triple.precondition
            try_command = triple.command.body # Commands inside the try block

            
            except_commands = triple.command.handlers # Commands inside the first except block
            # First get the postcondition for the try block
            try_completion = self.complete_triple_cot(Triple(pre, try_command, State.UNKNOWN), depth=depth+1, type = "try block")
            # Then get the postcondition for the except block
            # except_completion = self.complete_triple_cot(Triple(State.UNKNOWN, except_command, State.UNKNOWN),
                                                        #  depth=depth+1, type="except block")
            self.collected.append((str(try_completion), depth, "the try block", pprint_try_stmt(triple.command), True))
            # Handle multiple except blocks
            except_completions = []
            #keep the index of the except block\
            for handler, i in zip(triple.command.handlers, range(len(triple.command.handlers))):
                except_command = handler.body
                except_completion = self.complete_triple_cot(Triple(State.UNKNOWN, except_command, State.UNKNOWN), depth=depth+1, type=f"except block_{i+1}")
                except_completions.append(except_completion)
                self.collected.append((str(except_completion), depth, f"the except block {i+1}", pprint_except_stmt(handler), True))

            #for the except_completitions make them into one string saying that its one is the except number i
            except_completion = "\n".join([f"except_{i+1}: {exc}" for i, exc in enumerate(except_completions)])
            # Create a TryTriple to represent the try-except block and then compute the overall postcondition
            try_triple = TryTriple(pre, triple.command, try_command, try_completion, except_commands, except_completion,
                                   State.UNKNOWN)

            post = complete_try_triple(try_triple, self.model)

            #if we wanna merge the output state of the try catch block , currently not used
            # merged_output = merge_triple(Triple(post, triple.command, State.UNKNOWN), self.model)
            # post =merged_output

            current_index = self.index_stack.pop()
            #add to the current_index of the self.collected
            self.collected.insert(current_index,(str(post), depth, "a summary of the whole try-except block", "", False))

            # If we are inside a function and there's a return statement, collect the postcondition and we are done for this recursion
            if depth >= 1 and any(isinstance(node, ast.Return) for node in ast.walk(triple.command)):
                self.collected_returns.append((str(post),self.last_return_depth))
                self.last_return_depth=0
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
            #push the index of the current element in the collected list
            self.index_stack.append(len(self.collected))
            examples = []
            pre = triple.precondition
            # Unroll the loop by simulating 'k' iterations
            depth = depth + 1
            for i in range(k):
                self.collected.append(("", depth, f'Unrolled Loop {i+1}', "" ,True))
                post = self.complete_triple_cot(Triple(pre, body_command, State.UNKNOWN), depth=depth, type=f"unrolled_loop_{i+1}")
                self.collected.append((str(post), depth, f'the summary of unrolled_loop_{i+1}', "" , True))
                examples.append(Triple(pre, body_command, post))
                pre = get_precondition(self.model, post, while_head)
            depth = depth -1
            # Create a Triple for the entire 'while' loop
            triple = Triple(triple.precondition, triple.command, State.UNKNOWN)
            post = complete_loop_triple(triple, self.model, examples)
            body_commands = while_head + "\n"
            indent = " " * ((depth+1) * 4)
            for command in triple.command.body:
                body_commands= body_commands + f"{indent}{pprint_cmd(command)}"
            body_commands = body_commands + "\n" + f"{indent}# In the following comments we are unrolling the loop {k} times to help you understand its functionality\n"
            

            #if we wanna merge the output state of the if-else statement , currently not used
            # merged_output = merge_triple(Triple(post, triple.command, State.UNKNOWN), self.model)
            # post =merged_output

            current_index = self.index_stack.pop()    
            self.collected.insert(current_index,(str(post), depth, "a summary of the total loop", body_commands , False))
            if depth >= 1 and any(isinstance(node, ast.Return) for node in ast.walk(triple.command)):
                self.collected_returns.append((str(post),self.last_return_depth))
                self.last_return_depth=0
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
                self.collected_returns.append((self.last_return,self.last_return_depth))
                self.got_return = False
            if len(self.collected_returns) > 1:
                # add Case_{counter} to ecah return postcondition and new line at the end of it. but remember that the collected_returns is a list of tuples
                self.collected_returns = [f"Case_{i+1}: {ret[0]}\n" for i, ret in enumerate(self.collected_returns)]
            else:
                self.collected_returns = [f"Return: {ret[0]}\n" for ret in self.collected_returns]
            return_conditions_str = "\n".join(self.collected_returns)

            
           

            func_triple = FuncTriple(triple.precondition, triple.command, def_str, triple.command.body,
                                    return_conditions_str, State.UNKNOWN)
             #get the final reasoning from the llm
            final= complete_func_triple(func_triple, self.model)
            
            
            
            #append the final reasoning to the beggining of the collected list
            self.collected.append((str(final), depth, "the summary for the whole function",def_str , True))
            
            #sort the collected items by depth
            self.collected=sort_tasks_by_depth(self.collected)

            #pretty print the collected items
            total_code=pretty_print_tasks(self.collected)
            with open("tasks.txt", "a") as f:
                print(return_conditions_str, file =f)
            
            final = summarize_functionality_tree(total_code, final, self.model)
            return final
         
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
