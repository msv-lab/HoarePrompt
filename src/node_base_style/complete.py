import ast

from node_base_style.hoare_triple import State, Triple, IfTriple, FuncTriple, TryTriple, pprint_cmd, pprint_else_stmt, pprint_if_stmt, pprint_try_stmt, pprint_except_stmt
from node_base_style.general import complete_triple, complete_triple_batch
from node_base_style.print_triple import complete_print_triple
from node_base_style.if_statement import complete_if_triple
from node_base_style.function_definition import complete_func_triple, get_func_def
from node_base_style.loop import complete_loop_triple, get_while_head,get_for_loop_head, complete_loop_triple_0_unroll
from node_base_style.loop_1_unroll import complete_loop_triple_1_unroll
from node_base_style.for_loop import complete_for_triple, complete_for_triple_0_unroll
from node_base_style.for_loop_1_unroll import complete_for_triple_1_unroll
from node_base_style.loop_condition import get_precondition
from node_base_style.loop_condition_first import get_while_precondition_first
from node_base_style.for_condition import get_for_precondition
from node_base_style.for_condition_first import get_for_precondition_first
from node_base_style.try_statement import complete_try_triple
from node_base_style.task_sorter import sort_tasks_by_depth, sort_post_by_depth, print_tree
from node_base_style.merger import merge_triple
from node_base_style.tree import summarize_functionality_tree
from node_base_style.return_triple import complete_return_triple
from node_base_style.if_precondition import complete_if_precondition
from node_base_style.else_precondition import complete_else_precondition


class PostconditionAnalyzer:
    """
    Analyzes the postcondition of a program given its precondition and source code.
    Handles recursive analysis, collects postconditions, and manages specific cases like loops and returns.
    """
    
    def __init__(self, model, config):
        """
        Initialize the PostconditionAnalyzer with a model and configuration.
        """
        self.model = model
        self.config = config
        self.collected_returns = [] # Store postconditions from return statements as a list of tuples (postcondition, depth)
        self.collected=[] # General storage for collected postconditions, storing tuples (postcondition, depth, context, command, is_loop_related)

        # Flags and state trackers
        self.got_return = False              # Indicates if a return statement was encountered at the current recursion level
        self.last_return = ""                # Stores the last return postcondition
        self.last_return_depth = 0           # Depth of the last return statement
        self.index_stack = []                # Stack to store indices during recursion
        self.inside_loop = False             # Flag to indicate whether we're inside a loop
        self.last_loop_depth = 1000          # Depth of the last loop encountered, initalised with a high value so any loop will have a lower depth
        self.first_for = True                # Tracks if it's the first `for` loop in the current scope
        self.got_if_else_return = False      # Flag to indicate both `if` and `else` branches have unavoidable return statements

    # Check if a command is a simple statement (e.g., assignment, expression, etc.)
    def is_simple_statement(self,command):
        """Checks if a command is a simple statement, excluding print statements."""
        return isinstance(command, (ast.Assign, ast.AugAssign, ast.Raise, ast.Pass, ast.Break, ast.Continue)) or (
            isinstance(command, ast.Expr) and not self.is_print(command)
        )

    def is_print(self,command):
        """Checks if a command is a print statement in Python 3."""
        return (
            isinstance(command, ast.Expr) and 
            isinstance(command.value, ast.Call) and 
            isinstance(command.value.func, ast.Name) and 
            command.value.func.id == "print"
        )


    # Core recursive method to compute the postcondition of a Triple .
    def complete_triple_cot(self, triple: Triple, depth=0, type ="", annotate_prints=True ):
        """
        Core recursive method to compute the postcondition of a given Triple.

        Args:
            triple (Triple): The program triple containing precondition, command, and postcondition.
            depth (int): Current depth in the recursion tree.
            type (str): Context type for better understanding of the analysis (e.g., "if block").

        Returns:
            State: The computed postcondition.
        """

        #if the postcondition is already known, there was an error calling the function to compute it
        assert triple.postcondition == State.UNKNOWN

        # Generic case: Handle simple commands like assignments or expressions
        if self.is_simple_statement(triple.command):
            post = complete_triple(triple, self.model)
            
            # Collect the postcondition if not inside a loop
            if not self.inside_loop:
                context = f"simple command in {type}" if type else "simple command"
                self.collected.append((str(post), depth, context, pprint_cmd(triple.command), False))
            
            return post

        # Return case: Handle return statements
        if isinstance(triple.command, ast.Return):
            post = complete_return_triple(triple, self.model)
            # If we're at depth >= 1 (just inside function), collect the return postcondition.
            # If we are lower than depth 1, we are inside a loop or if statement , or try, so we don't collect the return postcondition, they will be collected in the higher level
            if depth >= 1:
                self.got_return = True
                self.last_return = str(post)
                self.last_return_depth = depth
                
                # Collect the return postcondition if not inside a loop
                if not self.inside_loop:
                    context = f"return statement in {type}" if type else "return statement"
                    self.collected.append((str(post), depth, context, pprint_cmd(triple.command), False))
                
            return post
        
        if self.is_print(triple.command):
            post = complete_print_triple(triple, self.model)
            
            # Collect the postcondition if not inside a loop
            if not self.inside_loop:
                context = f"print statement in {type}" if type else "print statement"
                self.collected.append((str(post), depth, context, pprint_cmd(triple.command), False))
            
            return triple.precondition


        # List case: Handle compound statements (e.g., function body or code blocks)
        # we dont really do anything here just analyse the blocks one by one by calling the complete_triple_cot recursively
        if isinstance(triple.command, list) and not self.config["concat_simple"]:
            pre = triple.precondition

            # Recursively compute the postcondition for each sub-command
            for subcmd in triple.command:
                completion = self.complete_triple_cot(Triple(pre, subcmd, State.UNKNOWN), depth=depth, type=type)
                pre = completion

                # Exit early if a return statement or both branches of an if-else have returns
                if self.got_return:
                    break
                if self.got_if_else_return:
                    print("Exiting due to complete if-else returns.")
                    self.got_if_else_return = False
                    break

            return pre
        

        if isinstance(triple.command, list) and self.config["concat_simple"]:
            pre = triple.precondition
            simple_commands = []

            for subcmd in triple.command:
                if self.is_simple_statement(subcmd):
                    # Collect simple commands in a batch
                    simple_commands.append(subcmd)
                else:
                    # Process the batch of simple commands if we encounter a non-simple command
                    if simple_commands:
                        # batch_input = "\n".join([pprint_cmd(cmd) for cmd in simple_commands])
                        # Call the LLM once for the entire batch
                        # print(f"I am analysing a batch of simple commands : {pprint_cmd(simple_commands)}")
                        post = complete_triple_batch(Triple(pre, simple_commands, State.UNKNOWN), self.model)

                        # Collect the postcondition for the commands in the batch
                    
                        if not self.inside_loop:
                            for cmd in simple_commands:
                                context = f"simple command in {type}" if type else "simple command"
                                self.collected.append((str(post), depth, context, pprint_cmd(cmd), False))
                        pre= post
                        simple_commands = []  # Reset the batch

                    # Recursively process the non-simple command
                    completion = self.complete_triple_cot(Triple(pre, subcmd, State.UNKNOWN), depth=depth, type=type)
                    pre = completion

                    # Exit early if a return statement or both branches of an if-else have returns
                    if self.got_return:
                        break
                    if self.got_if_else_return:
                        print("Exiting due to complete if-else returns.")
                        self.got_if_else_return = False
                        break

            # Process any remaining simple commands in the batch
            if simple_commands:
                # print(f"I am analysing a batch of simple commands : {pprint_cmd(simple_commands)}")
                pre = complete_triple_batch(Triple(pre, simple_commands, State.UNKNOWN), self.model)
                
                if not self.inside_loop:
                    for cmd in simple_commands:
                        context = f"simple command in {type}" if type else "simple command"
                        self.collected.append((str(pre), depth, context, pprint_cmd(cmd), False))
            return pre
            
        # If case : Handles the analysis of an AST `if-else` statement
        if isinstance(triple.command, ast.If):

            pre = triple.precondition
            condition = ast.unparse(triple.command.test)  # Extract the condition as a string
            self.got_if_else_return = False  # Reset the flag for if-else returns

            # Store the starting index of the `if` statement in the collected list
            self.index_stack.append(len(self.collected))
            
           
            # --- Handle the `if` branch ---
            extended_if_precondition = pre # Initialize the extended precondition for the `if` branch
            if self.first_for:
                # Extend precondition for the `if` condition if we are in the first unroll of a loop or not in a loop
                extended_if_precondition = complete_if_precondition(pre, f"if ({condition}):", self.model)

           # Compute the postcondition for the `if` branch
            if_post = self.complete_triple_cot(
                Triple(extended_if_precondition, triple.command.body, State.UNKNOWN), depth=depth + 1, type="if part"
            )
            if_return = is_return_unavoidable(triple.command.body) # Check if a return statement is unavoidable in the `if` branch


            if not self.inside_loop:
                self.collected.append(
                        (str(if_post), depth, "the if part of the statement", pprint_if_stmt(triple.command), True)
                    )

            
            
            # Collect return postconditions if present in the `if` branch
            if contains_return(triple.command.body) and self.got_return:
                self.got_return = False
                self.collected_returns.append((str(if_post), self.last_return_depth))
                self.last_return_depth = 0

            # --- Handle the `else` branch (if it exists) ---
            else_post = None
            else_return = False
            if triple.command.orelse:
                extended_else_precondition =pre

                if self.first_for: 
                    # Extend precondition for the `else` branch if we are not in a loop or if we are  in the first unroll of a loop
                    extended_else_precondition = complete_else_precondition(pre, f"if ({condition}):", self.model)
                
                # Compute the postcondition for the `else` branch
                else_post = self.complete_triple_cot(
                    Triple(extended_else_precondition, triple.command.orelse, State.UNKNOWN), depth=depth + 1, type="else part"
                )
                else_return = is_return_unavoidable(triple.command.orelse)


                if not self.inside_loop:
                    self.collected.append(
                            (str(else_post), depth, "the else statement of the if-else block", pprint_else_stmt(triple.command), True)
                        )
                
                # Collect return postconditions if present in the `else` branch
                if contains_return(triple.command.orelse) and self.got_return:
                    self.got_return = False
                    self.collected_returns.append((str(else_post), self.last_return_depth))
                    self.last_return_depth = 0

             # --- Compute the overall postcondition --- if necessary
            if_triple = IfTriple(pre, triple.command, if_post, else_post, State.UNKNOWN)

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
                else: # Single `if` branch without `else`
                    if not if_return: #single if statement with no return
                        post = complete_if_triple(if_triple, self.model)
                    else: #single if statement with return
                        post= complete_else_precondition(pre, f"if ({condition}):", self.model)

            
            #pop the  index of where the if statement starts from the stack . not used currently
            current_index = self.index_stack.pop()

            # Collect the summary for the entire `if-else` block
            if not self.inside_loop :
                if post == pre:
                    # If the postcondition is the same as the precondition, we don't need to print the entire if-else block
                    self.collected.append((str(post), depth, "a non printable summary of the whole if-else block", "", False))
                elif triple.command.orelse:
                    self.collected.append((str(post), depth, "a summary of the whole if-else block", "", False))
                else:
                    self.collected.append((str(post), depth, "a summary of the whole if block", "", False))
            
           
           # If both `if` and `else` branches return, set the flag
            if if_return and else_return:
                self.got_if_else_return = True
                
            return post

        # Case for try except blocks
        if isinstance(triple.command, ast.Try):
            
            pre = triple.precondition

            # Push the current index of `self.collected` into the stack, not currently used
            self.index_stack.append(len(self.collected))
               
            # --- Handle the `try` block ---
            try_commands = triple.command.body  # Commands inside the `try` block
            try_completion = self.complete_triple_cot(
                Triple(pre, try_commands, State.UNKNOWN), depth=depth + 1, type="try block"
            )
        
            
            if not self.inside_loop: #if we are not inside a loop
                self.collected.append((str(try_completion), depth, "the try block", pprint_try_stmt(triple.command), True))
            
            # --- Handle `except` blocks ---
            except_completions = []
            for i, handler in enumerate(triple.command.handlers):
                except_commands = handler.body  # Commands inside the current `except` block
                except_completion = self.complete_triple_cot(
                    Triple(State.UNKNOWN, except_commands, State.UNKNOWN), depth=depth + 1, type=f"except block_{i + 1}"
                )
                except_completions.append(except_completion)

                if not self.inside_loop:
                    self.collected.append((str(except_completion), depth, f"the except block {i+1}", pprint_except_stmt(handler), True))

             # Combine the results of all `except` blocks into a single string for clarity
            combined_except_postconditions = "\n".join(
                [f"except_{i + 1}: {exc}" for i, exc in enumerate(except_completions)]
            )

            # --- Compute the overall postcondition ---
            try_triple = TryTriple(
                pre, triple.command, try_commands, try_completion, triple.command.handlers, combined_except_postconditions, State.UNKNOWN
            )
            post = complete_try_triple(try_triple, self.model)


            #if we wanna merge the output state of the try catch block , currently not used
            # merged_output = merge_triple(Triple(post, triple.command, State.UNKNOWN), self.model)
            # post = merged_output

            
            current_index = self.index_stack.pop() #get the index of the whole try-except block and insert the postcondition there, not currently used
            # Collect a summary of the whole `try-except` block
            if not self.inside_loop: #if we are not inside a loop
                self.collected.append((str(post), depth, "a summary of the whole try-except block", "", False))

            # --- Handle Return Collection ---
            # Collect the postcondition if there's a `return` statement in the block
            if any(isinstance(node, ast.Return) for node in ast.walk(triple.command)) and self.got_return and depth ==1:
                self.collected_returns.append((str(post),self.last_return_depth))
                self.last_return_depth=0
                self.got_return = False
                
            return post
        

       

        # Case for for loops
        if isinstance(triple.command, ast.For):
            k = self.config["loop-unrolling-count"]  # Number of loop unrolls from the config
            body_command = triple.command.body  # The body of the for loop
            loop_head = get_for_loop_head(triple.command)  # The header of the for loop, e.g., `for x in y:`
            # iterator_var = triple.command.target  # The loop variable, e.g., `x` in `for x in y:`
            # iter_expression = triple.command.iter  # The iterable expression, e.g., `y` in `for x in y:`

             # Push the current index of `self.collected` into the stack, not used currently
            self.index_stack.append(len(self.collected))

            # Track the initial precondition and initialize the unrolled postconditions
            pre = triple.precondition
            original_pre = get_for_precondition_first(self.model, pre, loop_head)
            unrolled_post = ""
            examples = []  # Stores examples for each unrolled iteration

            indent = " " * ((depth + 1) * 4)  # Indentation for nested blocks
            self.inside_loop = True  # Flag to indicate we are inside a loop
            self.first_for = True  # Flag for the first unroll
            self.last_loop_depth = min(self.last_loop_depth, depth) #the highest level that there is a loop
            depth += 1  # Increment depth for nested structure

            # Unroll the loop `k` times
            for i in range(k):
                post = self.complete_triple_cot(
                    Triple(original_pre, body_command, State.UNKNOWN),
                    depth=depth,
                    type=f"unrolled_loop_{i + 1}"
                )
                unrolled_post = unrolled_post+f"{indent}#state of the program after unrolled loop {i+1}: {post} \n"
                examples.append(Triple(original_pre, body_command, post))

                # Update precondition for the next iteration , no need to do that for the last unroll since there is not gonna be next iteration
                if i < k-1:
                    original_pre = get_for_precondition(self.model, post, loop_head)
                self.first_for = False # we are no longer in the first unroll

            
            self.first_for = True # Reset first unroll flag
            depth -= 1  # Done with the loop, decrease depth

            if self.last_loop_depth == depth:  # we will say we are no loger in a loop only if we are sure this is the highest level loop we are in
                self.last_loop_depth = 1000
                self.inside_loop =  False # we are no longer inside a high level loop

            # Create a Triple for the entire for loop
            triple = Triple(triple.precondition, triple.command, State.UNKNOWN)
            #single unroll case
            if k==1:
                post = complete_for_triple_1_unroll(triple, self.model, examples)
            elif k==0: #no unroll case
                post = complete_for_triple_0_unroll(triple, self.model)
            else: #multiple unroll casse
                post = complete_for_triple(triple, self.model, examples)  # Aggregate the postconditions of the unrolled iterations

            # Prepare the code tree representation
            body_commands = pprint_cmd(body_command)
            body_commands = body_commands.replace("\n", "\n" + indent)
            loop_summary = loop_head + "\n" + indent + body_commands
            # Uncomment the following line if you want unrolled states in the code tree:
            # loop_summary += f"\n{indent}# Unrolling the for loop {k} times for comprehension\n{unrolled_post}"

            # Get the correct index of the self.collected list, not currently used
            current_index = self.index_stack.pop()

            # Store the summary of the entire loop in `self.collected`
            if not self.inside_loop: # if we are not inside a loop 
                self.collected.append((str(post), depth, "summary of total for loop", loop_summary, False))

            # Handle any return statements found within the loop
            if  any(isinstance(node, ast.Return) for node in ast.walk(triple.command)) and self.got_return and depth ==1:
                self.collected_returns.append((str(post), self.last_return_depth))
                self.last_return_depth = 0
                self.got_return = False
                
            return post


        # Case for while loops
        if isinstance(triple.command, ast.While):
            k = self.config["loop-unrolling-count"] # the unrolling param from the config
            while_head = get_while_head(triple.command)  # The loop header, e.g., `while condition:`
            body_command = triple.command.body  # The body of the `while` loop
        
            #push the index of the current element (so the index of the whole while loop) in the collected list, not currently used
            self.index_stack.append(len(self.collected))
            
           # Track the initial precondition and initialize the unrolled postconditions
            pre = triple.precondition
            original_pre = get_while_precondition_first(self.model, pre, while_head)
            unrolled_post = ""
            examples = []  # Stores examples for each unrolled iteration

            indent = " " * ((depth + 1) * 4)  # Indentation for nested blocks
            self.last_loop_depth = min(self.last_loop_depth, depth) #make the last loop depth the highest level there is a loop
            self.inside_loop = True  # Mark that we are inside a loop
            self.first_for = True  # Reset first unroll flag
            depth += 1  # Increment depth for nested structure

            # Unroll the loop `k` times
            for i in range(k):
                post = self.complete_triple_cot(
                    Triple(original_pre, body_command, State.UNKNOWN),
                    depth=depth,
                    type=f"unrolled_loop_{i + 1}"
                )                
                unrolled_post = unrolled_post+f"{indent}#state of the program after unrolled loop {i+1}: {post} \n"
                examples.append(Triple(original_pre, body_command, post))

                # Update precondition for the next iteration, only if we are not at the last unroll
                if i < k-1:
                    original_pre = get_precondition(self.model, post, while_head)
                self.first_for = False

            self.first_for = True # Reset first unroll flag
            depth = depth -1 # we are done with the loop so decrease the depth by 1

            if self.last_loop_depth == depth: # we will say we are no loger in a loop only if we are sure this is the highest level loop we are in
                self.last_loop_depth = 1000
                self.inside_loop =  False # we are no longer inside a high level loop

            # Create a Triple for the entire 'while' loop
            triple = Triple(triple.precondition, triple.command, State.UNKNOWN)
            # Compute the overall postcondition for the entire loop, depending on if unroll =1 or multiple
            if k==1:
                post = complete_loop_triple_1_unroll(triple, self.model, examples)
            elif k==0:
                post = complete_loop_triple_0_unroll(triple, self.model)
            else:
                post = complete_loop_triple(triple, self.model, examples)
            
            # Prepare the code tree representation
            body_commands = pprint_cmd(body_command)
            body_commands = body_commands.replace("\n", "\n" + indent)
            loop_summary = while_head + "\n" + indent + body_commands
            # Uncomment the following line if you want unrolled states in the code tree:
            # loop_summary += f"\n{indent}# In the following comments, we unroll the loop {k} times to help you understand its functionality\n{unrolled_post}"

            # if we wanna merge the output state of the if-else statement , currently not used
            # merged_output = merge_triple(Triple(post, triple.command, State.UNKNOWN), self.model)
            # post = merged_output

            # pop the correct index of the self.collecte dlist, not currently used
            current_index = self.index_stack.pop()    

            if not self.inside_loop: # if we are not inside a loop 
                self.collected.append((str(post), depth, "a summary of the total loop", loop_summary , False))
            
            # Handle any return statements inside the loop
            if any(isinstance(node, ast.Return) for node in ast.walk(triple.command)) and self.got_return and depth ==1:
                self.collected_returns.append((str(post),self.last_return_depth))
                self.last_return_depth=0
                self.got_return = False
                
            return post

        # Case for function definitions
        if isinstance(triple.command, ast.FunctionDef):
            #initialise all the values, probably unnecessary since it is done when creating a postoncition analyser
            self.collected_returns = []  #initialise the return lis
            self.collected=[] #initialise the postocniditons list
            self.got_return = False # Flag to check if a return statement was encountered in the same level of recursion
            self.last_return ="" # the last return statement
            self.last_return_depth=0 # the depth of the last return statement
            self.index_stack=[] #creates a stack to store the current index
            self.inside_loop= False #flag to check if we are inside a loop


            pre = triple.precondition
            def_str = get_func_def(triple.command) # Get the function signature (the name plus input params of the func) as a string
            
            # Analyze the function body recursively
            self.complete_triple_cot(Triple(pre, triple.command.body, State.UNKNOWN), depth=1)

            # Handle unprocessed return conditions
            if self.got_return:
                self.collected_returns.append((self.last_return, self.last_return_depth))
                self.got_return = False

             # Format return conditions for multiple cases
            if len(self.collected_returns) > 1:
                self.collected_returns = [f"Case_{i+1}: {ret[0]}\n" for i, ret in enumerate(self.collected_returns)]
            else:
                self.collected_returns = [f"{ret[0]}\n" for ret in self.collected_returns]
            return_conditions_str = "\n".join(self.collected_returns)

            # Create a FuncTriple for the entire function
            func_triple = FuncTriple(triple.precondition, triple.command, def_str, triple.command.body,
                                    return_conditions_str, State.UNKNOWN)
            
            # Generate the function reasoning using the LLM
            final= complete_func_triple(func_triple, self.model)
            
            
            # Append the reasoning to the collected items
            self.collected.append((str(final).strip(), depth, "the summary for the whole function",def_str , True))
            
            # Sort and format the collected items
            self.collected = sort_tasks_by_depth(self.collected)
            total_code = sort_post_by_depth(self.collected)
            
            total_tree = print_tree(total_code, annotate_prints)

            # Debugging: Save return conditions to a file
            # with open("tasks.txt", "a") as f:
            #     print(return_conditions_str, file =f)
            
            # Add precondition as a comment at the beginning of the tree
            total_tree = f"#State of the program right berfore the function call: {pre}\n" + total_tree

            # Summarize functionality and integrate it into the code tree
            final = summarize_functionality_tree(total_tree, return_conditions_str, self.model)
            updated_total_tree = replace_functionality(total_tree, final)

            return (final, return_conditions_str, updated_total_tree)
         
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
    if "annotate_prints" in config:
        annotate_prints = config["annotate_prints"]
    else:
        annotate_prints = True
    postcondition = analyzer.complete_triple_cot(triple, annotate_prints=annotate_prints)
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
