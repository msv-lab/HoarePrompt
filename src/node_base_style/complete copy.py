import ast

from node_base_style.hoare_triple import State, Triple, IfTriple, FuncTriple, TryTriple, pprint_cmd, pprint_else_stmt, pprint_if_stmt, pprint_try_stmt, pprint_except_stmt, pprint_else_stmt2, pprint_if_else
from node_base_style.general import complete_triple
from node_base_style.if_statement import complete_if_triple
from node_base_style.function_definition import complete_func_triple, get_func_def
from node_base_style.loop import complete_loop_triple, get_while_head,get_for_loop_head, ForToWhileTransformer
from node_base_style.loop_1_unroll import complete_loop_triple_1_unroll
from node_base_style.for_loop import complete_for_triple
from node_base_style.for_loop_1_unroll import complete_for_triple_1_unroll
from node_base_style.loop_condition import get_precondition
from node_base_style.loop_condition_first import get_while_precondition_first
from node_base_style.for_condition import get_for_precondition
from node_base_style.for_condition_first import get_for_precondition_first
from node_base_style.try_statement import complete_try_triple
from node_base_style.task_sorter import sort_tasks_by_depth, pretty_print_tasks, sort_post_by_depth, print_tree
from node_base_style.merger import merge_triple
from node_base_style.tree import summarize_functionality_tree
from node_base_style.return_triple import complete_return_triple
from node_base_style.if_precondition import complete_if_precondition
from node_base_style.else_precondition import complete_else_precondition


# This is a class responsible for analyzing the postcondition of a program given its precondition and source code
class PostconditionAnalyzer:
    def __init__(self, model, config):
        self.model = model
        self.config = config
        # Collects postconditions from return statements as strings. but i also want it to collect the depth for each postcondition so a list of tuples
        self.collected_returns = []
        self.collected=[]
        self.got_return = False # Flag to check if a return statement was encountered in the same level of recursion
        self.last_return ="" # the last return statement
        self.last_return_depth=0 # the depth of the last return statement
        self.index_stack=[] #creates a stack to store the current index
        self.inside_loop= False #flag to check if we are inside a loop
        self.last_loop_depth = 1000 # the depth of the last loop statement
        self.first_for = True
        self.got_if_else_return = False #if both the if and the else branch have unavoidable return statements
        
    # Core recursive method to compute the postcondition of a Triple .
    def complete_triple_cot(self, triple: Triple, depth=0, type ="") :
        assert triple.postcondition == State.UNKNOWN

        #generic easy case
        if isinstance(triple.command,
                      (ast.Assign, ast.AugAssign, ast.Expr, ast.Raise, ast.Pass, ast.Break, ast.Continue)):
            post = complete_triple(triple, self.model)
            print(f"We are analysing a simple command: {pprint_cmd(triple.command)}")
            if not self.inside_loop: # if we are not inside a loop
                if type != "":
                    self.collected.append((str(post), depth, f"simple command in {type}", pprint_cmd(triple.command), False))
                else:
                    self.collected.append((str(post), depth, "simple command", pprint_cmd(triple.command), False))
            return post

        # Handle return statements
        if isinstance(triple.command, ast.Return):
            post = complete_return_triple(triple, self.model)
            # If we're at the first level of depth (inside a function), collect the return postcondition and we are done for this recursion
            if depth >= 1 :
                self.got_return = True # we got a return statement
                self.last_return = str(post) # the last return statement
                self.last_return_depth= depth # the depth of the last return statement
                if not self.inside_loop: # if we are not inside a loop
                    if type != "":
                        self.collected.append((str(post), depth, f"return statement in {type}", pprint_cmd(triple.command),False))
                    else:
                        self.collected.append((str(post), depth, "return statement", pprint_cmd(triple.command), False))
                return post
                #self.collected_returns.append(str(post))
            return post

        # case where there are multiple statements, like a function body or a block of code
        # we dont really do anything here just analyse the blocks one by one by calling the complete_triple_cot recursively
        if isinstance(triple.command, list):
            pre = triple.precondition
            # Recursively compute the postcondition for each sub-command
            for subcmd in triple.command:
                completion = self.complete_triple_cot(Triple(pre, subcmd, State.UNKNOWN), depth=depth, type=type)
                pre = completion
                #self.collected.append((str(completion), depth))
                if self.got_return:
                    break
                if self.got_if_else_return:
                    print("Wassup")
                    self.got_if_else_return = False
                    break
            return pre
        
        # Case for if statements
        if isinstance(triple.command, ast.If):
            pre = triple.precondition
            self.got_if_else_return = False 
            
            condition = ast.unparse(triple.command.test)
            
            if_return = False
            #push the current index of the  self.collected list in the current stack
            self.index_stack.append(len(self.collected))
            extended_if_precondition= pre
            if self.first_for:
                extended_if_precondition = complete_if_precondition(pre, f"if ({condition}):", self.model)
            # Find the postcondition for the if body
            then_completion = self.complete_triple_cot(Triple(extended_if_precondition, triple.command.body, State.UNKNOWN), depth=depth+1, type="if part")
            if_post = then_completion
            if_return = is_return_unavoidable(triple.command.body)

            if not self.inside_loop :
                if if_return:
                    # print("AAAAAAAAAAAAAAAAAAAAAAAA")
                    self.collected.append((str(if_post), depth, "the if part of the statement", pprint_if_stmt(triple.command), True))
                else:
                    # print("CCCCCCCCCCCCCCCCCCCC")
                    self.collected.append((str(if_post), depth, "the if part of the statement", pprint_if_stmt(triple.command), True))
            
            #if we are inside an if statement and there's a return statement, collect the postcondition and we are done for this recursion
            # if depth >= 1 and any(isinstance(node, ast.Return) for node in ast.walk(triple.command)) and self.got_return:
            #     self.got_return = False
            #     self.collected_returns.append((str(if_post),self.last_return_depth))
            #     self.last_return_depth=0
            if contains_return(triple.command.body)  and self.got_return:
                self.got_return = False
                self.collected_returns.append((str(if_post),self.last_return_depth))
                self.last_return_depth=0

            else_return =False
            else_post = None
            if triple.command.orelse:

                extended_else_precondition =pre
                if self.first_for:
                    extended_else_precondition= complete_else_precondition(pre, f"if ({condition}):", self.model)
                
                else_completion = self.complete_triple_cot(Triple(extended_else_precondition, triple.command.orelse, State.UNKNOWN),
                                                           depth=depth+1, type="else part")
                else_post = else_completion
                else_return = is_return_unavoidable(triple.command.orelse)

                if not self.inside_loop :
                    if else_return:
                        # print("BBBBBB")
                        self.collected.append((str(else_post), depth, "the else statement of the if-else block", pprint_else_stmt(triple.command), True))
                    else:
                        # print("DDDDDDDDDDDDDDD")
                        self.collected.append((str(else_post), depth, "the else statement of the if-else block", pprint_else_stmt(triple.command), True))
                # If we are inside a else  and there's a return statement, collect the postcondition and we are done for this recursion
                # if depth >= 1 and any(isinstance(node, ast.Return) for node in ast.walk(triple.command)) and self.got_return:
                #     self.got_return = False
                #     self.collected_returns.append((str(else_post),self.last_return_depth))
                #     self.last_return_depth=0
                
                if contains_return(triple.command.orelse) and self.got_return:
                    self.got_return = False
                    self.collected_returns.append((str(else_post),self.last_return_depth))
                    self.last_return_depth=0

            # Create an IfTriple to represent the if statement with its branches and then compute the overall post condition
            if_triple = IfTriple(pre, triple.command, if_post, else_post, State.UNKNOWN)
            # print("AAAAAAA")
            # print(pprint_if_stmt(triple.command))
            # print("BBBBBBBBB")
            # print(pprint_else_stmt(triple.command))
            # print("CCCCCCCCC")
            # print(pprint_if_else(triple.command))
            # print("DDDDDDDDDD")
            # print(pprint_cmd(triple.command))
            # print("EEEEEEEEEE")

            #if we are inside 2nd or 3rd iteration of loop lets do it the traditional way
            if not self.first_for:
                post = complete_if_triple(if_triple, self.model)
            else:
                if triple.command.orelse: #there is an else
                    #if only the if statement has high level return then we use only the else postcondition
                    if if_return and not else_return:
                        post = else_post
                    #if only the else statement has high level return then we use only the if postcondition
                    elif else_return and not if_return:
                        post = if_post
                    #if both have high level return then we use the precondition as the postcondition
                    elif else_return and if_return:
                        post = pre
                    else:
                        post = complete_if_triple(if_triple, self.model)
                else: #there is no else
                    if not if_return: #single if statement with no return
                        post = complete_if_triple(if_triple, self.model)
                    else: #single if statement with return
                        post= complete_else_precondition(pre, f"if ({condition}):", self.model)

            #if this was an if -else statement keep the postcondition for the total if -else otherwise we insert it with type if-statement
            
            #if we wanna merge the output state of the if-else statement , currently not used .This uses the merge.py and could be used for example in longer postconditions
            # merged_output = merge_triple(Triple(post, triple.command, State.UNKNOWN), self.model)
            # post = merged_output
            
            #pop the  index of where the if statement starts from the stack
            current_index = self.index_stack.pop()
            if not self.inside_loop :
                if post == pre:
                    self.collected.append((str(post), depth, "a non printable summary of the whole if-else block", "", False))
                elif triple.command.orelse:
                    self.collected.append((str(post), depth, "a summary of the whole if-else block", "", False))
                else:
                    self.collected.append((str(post), depth, "a summary of the whole if block", "", False))
            
           
            # If we are inside a function and there's a return statement, collect the postcondition and we are done for this recursion
            if if_return and else_return:
                self.got_if_else_return = True
                
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
            
            if not self.inside_loop: #if we are not inside a loop
                self.collected.append((str(try_completion), depth, "the try block", pprint_try_stmt(triple.command), True))
            # Then get the postcondition for the except block and handle multiple except blocks
            except_completions = []
            for handler, i in zip(triple.command.handlers, range(len(triple.command.handlers))):
                except_command = handler.body
                except_completion = self.complete_triple_cot(Triple(State.UNKNOWN, except_command, State.UNKNOWN), depth=depth+1, type=f"except block_{i+1}")
                except_completions.append(except_completion)
                if not self.inside_loop:
                    self.collected.append((str(except_completion), depth, f"the except block {i+1}", pprint_except_stmt(handler), True))

            #for the except_completitions make them into one string saying that each one is the except number i
            except_completion = "\n".join([f"except_{i+1}: {exc}" for i, exc in enumerate(except_completions)])
            # Create a TryTriple to represent the try-except block and then compute the overall postcondition
            try_triple = TryTriple(pre, triple.command, try_command, try_completion, except_commands, except_completion,
                                   State.UNKNOWN)

            #get the postoncdition for the whole try-except block
            post = complete_try_triple(try_triple, self.model)

            #if we wanna merge the output state of the try catch block , currently not used
            # merged_output = merge_triple(Triple(post, triple.command, State.UNKNOWN), self.model)
            # post = erged_output

            #get the index of the whole try-except block and insert the postcondition there
            current_index = self.index_stack.pop()
            if not self.inside_loop: #if we are not inside a loop
                self.collected.append((str(post), depth, "a summary of the whole try-except block", "", False))

            # If we are inside a function and there's a return statement, collect the postcondition and we are done for this recursion
            if any(isinstance(node, ast.Return) for node in ast.walk(triple.command)) and self.got_return and depth ==1:
                self.collected_returns.append((str(post),self.last_return_depth))
                self.last_return_depth=0
                self.got_return = False
                
            return post
        

        # This is a tricky case. If the command is a for loop, we need to convert it to a while loop and then compute the postcondition
        # if isinstance(triple.command, ast.For):
        #     t = ForToWhileTransformer()
        #     while_code = t.visit(triple.command)
        #     new_triple = Triple(triple.precondition, while_code, State.UNKNOWN)
        #     return self.complete_triple_cot(new_triple, depth=depth)

        # Case for for loops
        if isinstance(triple.command, ast.For):
            k = self.config["loop-unrolling-count"]  # The unrolling parameter from the config
            body_command = triple.command.body  # The body of the for loop
            loop_head = get_for_loop_head(triple.command)  # The header of the for loop, e.g., `for x in y:`

            # Push the current element's index (entire for loop) into the index stack
            self.index_stack.append(len(self.collected))

            # List to store examples of unrolled runs of the loop
            examples = []
            
            pre = triple.precondition
            iterator_var = triple.command.target  # The loop variable, e.g., `x` in `for x in y:`
            iter_expression = triple.command.iter  # The iterable expression, e.g., `y` in `for x in y:`

            # Generate the initial state of the loop variable for unrolling
            original_pre =get_for_precondition_first(self.model, pre, loop_head)
            indent = " " * ((depth + 1) * 4)
            unrolled_post = ""
            
            self.inside_loop = True  # Mark that we are inside a loop to avoid annotation in the code tree
            self.first_for = True # we are in the first unroll
            self.last_loop_depth = min(self.last_loop_depth, depth)
            depth += 1  # Increase depth since we’re inside the loop
            for i in range(k):
                post = self.complete_triple_cot(Triple(original_pre, body_command, State.UNKNOWN), depth=depth, type=f"unrolled_loop_{i+1}")
                unrolled_post = unrolled_post+f"{indent}#state of the program after unrolled loop {i+1}: {post} \n"
                examples.append(Triple(original_pre, body_command, post))
                if i < k-1:
                    original_pre = get_for_precondition(self.model, post, loop_head)
                self.first_for = False
            self.first_for = True

            depth -= 1  # Done with the loop, decrease depth
            if self.last_loop_depth == depth:
                self.last_loop_depth = 1000
                self.inside_loop =  False # we are no longer inside a high level loop

            # Create a Triple for the entire for loop
            triple = Triple(triple.precondition, triple.command, State.UNKNOWN)
            if k==1:
                post = complete_for_triple_1_unroll(triple, self.model, examples)
            else:
                post = complete_for_triple(triple, self.model, examples)  # Aggregate the postconditions of the unrolled iterations

            # Format loop body for code tree output with indentation and postconditions
            body_commands = pprint_cmd(body_command)
            body_commands = body_commands.replace("\n", "\n" + indent)
            # Insert comments for unrolled states within the code tree
            #uncomment the following line if you want the unrolled postconditions to be in the code tree
            # body_commands = loop_head + "\n" + indent + body_commands + f"# Unrolling the for loop {k} times for comprehension\n{unrolled_post}"
            body_commands = loop_head + "\n" + indent + body_commands 
            # Store the summary of the whole loop in the code tree at the correct index
            current_index = self.index_stack.pop()
            
            if not self.inside_loop: # if we are not inside a loop 
                self.collected.append((str(post), depth, "summary of total for loop", body_commands, False))

            # Handle any return statements found within the loop
            if  any(isinstance(node, ast.Return) for node in ast.walk(triple.command)) and self.got_return and depth ==1:
                self.collected_returns.append((str(post), self.last_return_depth))
                self.last_return_depth = 0
                self.got_return = False
                
            return post


        # Case for while loops
        if isinstance(triple.command, ast.While):
            k = self.config["loop-unrolling-count"] # the unrolling param from the config
            body_command = triple.command.body # the body of the while loop
            while_head = get_while_head(triple.command) # the head of the while loop
            #push the index of the current element (so the index of the whole while loop) in the collected list
            self.index_stack.append(len(self.collected))
            
            #list to store the examples of unrolled runs of the loop
            examples = []
            
            pre = triple.precondition
            original_pre = get_while_precondition_first(self.model, pre, while_head) # get the initial state of the loop for unrolling
            # Unroll the loop by simulating 'k' iterations
            self.last_loop_depth = min(self.last_loop_depth, depth)
            self.inside_loop = True # we are inside a loop, so any postocnditions of the unrolled code should not be appended as annotations in the code tree
            self.first_for = True
            unrolled_post=""
            indent = " " * ((depth+1) * 4)
            depth = depth + 1 # increase the depth by 1 since we are inside a loop
            for i in range(k):
                post = self.complete_triple_cot(Triple(original_pre, body_command, State.UNKNOWN), depth=depth, type=f"unrolled_loop_{i+1}")
                unrolled_post = unrolled_post+f"{indent}#state of the program after unrolled loop {i+1}: {post} \n"
                examples.append(Triple(original_pre, body_command, post))
                if i < k-1:
                    original_pre = get_precondition(self.model, post, while_head)
                self.first_for = False
            self.first_for = True
                
            depth = depth -1 # we are done with the loop so decrease the depth by 1
            if self.last_loop_depth == depth:
                self.last_loop_depth = 1000
                self.inside_loop =  False # we are no longer inside a high level loop

            # Create a Triple for the entire 'while' loop
            triple = Triple(triple.precondition, triple.command, State.UNKNOWN)
            if k==1:
                post = complete_loop_triple_1_unroll(triple, self.model, examples)
            else:
                post = complete_loop_triple(triple, self.model, examples)
            
            body_commands = pprint_cmd(body_command)
            
            body_commands = body_commands.replace("\n", "\n"+indent) #replace all nwe lines with indent + new line
            # we are creating the whole loop for the code tree, with postconditions of every total unroll but without the code of the loop unrolled
            #uncomment the following line if you want the unrolled postconditions to be in the code tree
            # body_commands = while_head + "\n" +indent+ body_commands + f"# In the following comments we are unrolling the loop {k} times to help you understand its functionality\n {unrolled_post}"
            body_commands = while_head + "\n" +indent+ body_commands 
            #if we wanna merge the output state of the if-else statement , currently not used
            # merged_output = merge_triple(Triple(post, triple.command, State.UNKNOWN), self.model)
            # post =merged_output

            # store the summary of the whole loop in the code tree at the correct index
            current_index = self.index_stack.pop()    
            if not self.inside_loop: # if we are not inside a loop 
                self.collected.append((str(post), depth, "a summary of the total loop", body_commands , False))
            if any(isinstance(node, ast.Return) for node in ast.walk(triple.command)) and self.got_return and depth ==1:
                self.collected_returns.append((str(post),self.last_return_depth))
                self.last_return_depth=0
                self.got_return = False
                

            return post

        # Case for function definitions
        if isinstance(triple.command, ast.FunctionDef):
            self.collected_returns = []
            self.collected=[]
            self.got_return = False # Flag to check if a return statement was encountered in the same level of recursion
            self.last_return ="" # the last return statement
            self.last_return_depth=0 # the depth of the last return statement
            self.index_stack=[] #creates a stack to store the current index
            self.inside_loop= False #flag to check if we are inside a loop
            pre = triple.precondition
            def_str = get_func_def(triple.command) # Get the function signature (the name plus input params of the func) as a string
            
            #this is where the main job is being done by iterating over the body of the function
            self.complete_triple_cot(Triple(pre, triple.command.body, State.UNKNOWN), depth=1)

            #if the got_return flag is True then the last_return has not been appended to the collected_returns
            if self.got_return:
                self.collected_returns.append((self.last_return,self.last_return_depth))
                self.got_return = False
            if len(self.collected_returns) > 1:
                # add Case_{counter} to ecah return postcondition and new line at the end of it. but remember that the collected_returns is a list of tuples
                self.collected_returns = [f"Case_{i+1}: {ret[0]}\n" for i, ret in enumerate(self.collected_returns)]
            else:
                self.collected_returns = [f"{ret[0]}\n" for ret in self.collected_returns]
            return_conditions_str = "\n".join(self.collected_returns)

            
           

            func_triple = FuncTriple(triple.precondition, triple.command, def_str, triple.command.body,
                                    return_conditions_str, State.UNKNOWN)
            
            #get the complete function reasoning from the llm
            final= complete_func_triple(func_triple, self.model)
            
            
            #append the final reasoning to the beggining of the collected list
            self.collected.append((str(final).strip(), depth, "the summary for the whole function",def_str , True))
            
            #sort the collected items by depth
            self.collected=sort_tasks_by_depth(self.collected)
            
            #pretty print the collected items
            total_code=sort_post_by_depth(self.collected)
           
            total_code=print_tree(total_code)
            

            #Store the return conditions in a file for debugging
            with open("tasks.txt", "a") as f:
                print(return_conditions_str, file =f)
            
            #add the precondition to the tree as comment in the begining
            total_code = f"#State of the program right berfore the function call: {pre}\n" + total_code

            final = summarize_functionality_tree(total_code, return_conditions_str, self.model)
            updated_total_code = replace_functionality(total_code, final)
            return (final, return_conditions_str, updated_total_code)
         
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



def is_return_unavoidable(command):
    """
    Check if every path through the given AST node includes a `return` statement.
    If there exists at least one path without a `return`, return False.
    Otherwise, return True.
    """
    def path_avoids_return(node_or_statements):
        """
        Recursively check if there's a path through the given AST node or list of statements
        that avoids encountering a return statement.
        """
        # Handle a single node or a list of nodes
        if isinstance(node_or_statements, list):
            # Process each statement in the list
            for stmt in node_or_statements:
                if not path_avoids_return(stmt):
                    return False
            return True
        elif isinstance(node_or_statements, ast.Return):
            # This path encounters a return
            return False
        elif isinstance(node_or_statements, (ast.If, ast.While, ast.For)):
            # Check both the body and the orelse (if any)
            body_avoids = path_avoids_return(node_or_statements.body)
            orelse_avoids = path_avoids_return(node_or_statements.orelse)
            # If neither the body nor the orelse avoids a return, the path is terminal
            return body_avoids or orelse_avoids
        elif isinstance(node_or_statements, ast.FunctionDef):
            # Ignore nested function definitions
            return True
        elif isinstance(node_or_statements, (ast.Break, ast.Continue)):
            # Break or continue does not prevent further execution
            return True
        elif hasattr(node_or_statements, 'body'):
            # General case for nodes with a body attribute (e.g., Module, ClassDef)
            return path_avoids_return(node_or_statements.body)
        else:
            # Other nodes allow execution to continue
            return True

    # Handle the top-level input
    if isinstance(command, list):
        # If the input is a list, process each node
        return not path_avoids_return(command)
    elif isinstance(command, ast.AST):
        # If the input is a single AST node, process it directly
        return not path_avoids_return([command])
    else:
        raise ValueError("Input must be an ast.AST or a list of ast.AST nodes.")
    
def contains_return(body):
    """
    Check if an AST node or a list of AST nodes contains a Return statement.
    """
    if isinstance(body, list):
        # Wrap the list in an artificial container node like `ast.Module`
        container = ast.Module(body=body, type_ignores=[])
    elif isinstance(body, ast.AST):
        # Use the node as-is if it's already an AST node
        container = body
    else:
        raise ValueError("Input must be an ast.AST node or a list of ast.AST nodes.")

    # Use ast.walk to check for the presence of a Return node
    return any(isinstance(node, ast.Return) for node in ast.walk(container))



def replace_functionality(tree: str, functionality: str) -> str:
    # Define the marker line after which we want to replace content
    marker = "#Overall this is what the function does:"
    
    # Find the position of the marker in the tree
    marker_pos = tree.find(marker)
    
    # If the marker is not found, return the original tree without modifications
    if marker_pos == -1:
        return tree
    
    # Extract the part of the tree up to (and including) the marker
    before_marker = tree[:marker_pos + len(marker)]
    
    # Combine the content before the marker with the new functionality
    modified_tree = before_marker  + functionality.strip()
    
    return modified_tree
