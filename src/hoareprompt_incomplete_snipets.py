import argparse
import shutil
import json
import os
import sys
from pathlib import Path
from model import get_model

import precondition_extractor
import precondition_extractor_multi_func
import entailment
import entailment_no_fsl
import entailment_mult_func
import entailment_mult_func_no_fsl
import entailment_annotated
import entailement_mult_func_annotated
import comment_style
import code_completor
import precondition_extractor_incomplete
import node_base_style.complete_incomplete_snippets
from  node_base_style.naive import naive_question, naive_question_with_response
from node_base_style.naive_no_fsl import naive_question_no_fsl, naive_question_no_fsl_confidence, naive_question_no_fsl_confidence_2, naive_question_no_fsl_with_response, naive_question_no_fsl_confidence_qwen
from node_base_style.annotated_simple import annotated_simple
from node_base_style.single_post import single_post
from node_base_style.single_post_no_fsl import single_post_no_fsl
from verify_entailement import verify_tree ,verify_function_summary

import cex_generator
from textwrap import dedent
import ast

import re
from testing_equivalence import assess_postcondition_equivalence


def load_test_cases(file_path):
    """Load test cases from a JSON file."""
    with open(file_path, "r") as f:
        return json.load(f)




def ensure_parsable_program(snippet: str) -> str:
    """
    Ensures that an incomplete Python program snippet is parsable by:
    - Handling the global code or wrapping it into a function.
    - Ensuring middle functions are valid and complete.
    - Adding placeholders for incomplete blocks and endings.
    - Trimming empty lines and comments at the beginning of the snippet.

    :param snippet: A string containing the incomplete Python program snippet.
    :return: A modified, parsable Python program.
    """


    def remove_comments(line):
        """
        Removes the comment part of a line while preserving # inside string literals.
        """
        in_string = False
        escaped = False
        for i, char in enumerate(line):
            if char == "\\":
                escaped = not escaped
            elif char in ('"', "'"):
                if not escaped:
                    in_string = not in_string
                escaped = False
            elif char == "#" and not in_string:
                # This is the start of a comment
                return line[:i].rstrip()
            else:
                escaped = False
        return line
    def trim_empty_comments_and_imports(lines):
        """
        Remove leading empty lines, comments, and multiline string comments from the snippet.
        Extract import statements as a separate string.
        
        :param lines: List of lines from the code snippet.
        :return: Tuple (trimmed_lines, imports).
        """
        trimmed_lines = []
        imports = []
        inside_multiline = False

        for line in lines:
            stripped = line.strip()

            # Skip multiline comments
            if stripped.startswith(('"""', "'''")):
                if inside_multiline:
                    inside_multiline = False
                else:
                    inside_multiline = True
                continue
            if inside_multiline:
                continue

            # Skip empty lines and single-line comments
        
            if not stripped or stripped.startswith("#"):
                continue

            #remove the part of a line after #
            line = remove_comments(line)

            # Extract import statements
            if stripped.startswith(("import ", "from ")):
                imports.append(line)
                continue

            trimmed_lines.append(line)
        if len(imports) > 0:
            imports_str = "\n".join(imports) + "\n"
        else:
            imports_str = ""

        return trimmed_lines, imports_str


    def detect_global_or_function_start(lines):
        """
        Detect whether the start of the code is global or part of a function.
        """
        for line in lines:
            if line.lstrip().startswith("def "):
                return "function_start"
            elif not line.startswith(" "):
                return "global_start"
        return "code_start"

    def wrap_global_code(lines):
        """
        Wrap non-function code into a placeholder function.
        """
        return ["def function1():"] + [line for line in lines]
    
    def process_first_part(first_part_lines, remaining_lines):
        """
        Process the first part of the code snippet to handle global or function code.
        If the code starts with `else`, `elif`, or `except`, add a placeholder block.
        Otherwise, handle indentation issues by removing one level of indentation
        until a line with no indentation is found.
        """
        

        # Check if the first line starts with an incomplete block
        if first_part_lines and first_part_lines[0].strip().startswith(("else", "elif", "except")):
            # Add a placeholder for missing block
            if first_part_lines[0].strip().startswith("else"):
                placeholder = "if condition:  # ADDED_LINE\n    pass # ADDED_LINE\n"
            elif first_part_lines[0].strip().startswith("elif"):
                placeholder = "if condition: # ADDED_LINE\n    pass # ADDED_LINE\n"
            elif first_part_lines[0].strip().startswith("except"):
                placeholder = "try: # ADDED_LINE\n    pass # ADDED_LINE\n"
            return placeholder + "\n".join(first_part_lines) + "\n" + "\n".join(remaining_lines)

        # Handle indentation issues
        # If the code doesn't start with a block keyword, remove one level of indentation
        for i, line in enumerate(first_part_lines):
            if not line.startswith(" "):
                break
            # Check if the line has no indentation
            if i > 0:
                first_part_lines = [line[4:] if line.startswith("    ") else line for line in first_part_lines]
                break
        print(f"First part lines after processing: {first_part_lines}")
        # Combine the processed first part with the remaining lines
        first_part_str= "\n".join(first_part_lines)
        remaining_part_str= "\n".join(remaining_lines)
        return first_part_str + "\n" + remaining_part_str

    def process_first_part_unwrapped(first_part_lines):
        """
        Process the first part of the code snippet to handle global or function code.
        If the code starts with `else`, `elif`, or `except`, add a placeholder block.
        Otherwise, handle indentation issues by removing one level of indentation
        until a line with no indentation is found.
        """
        

        # Check if the first line starts with an incomplete block
        if first_part_lines and first_part_lines[0].strip().startswith(("else", "elif", "except")):
            # Add a placeholder for missing block
            if first_part_lines[0].strip().startswith("else"):
                placeholder = "if condition:  # ADDED_LINE\n    pass # ADDED_LINE\n"
            elif first_part_lines[0].strip().startswith("elif"):
                placeholder = "if condition: # ADDED_LINE\n    pass # ADDED_LINE\n"
            elif first_part_lines[0].strip().startswith("except"):
                placeholder = "try: # ADDED_LINE\n    pass # ADDED_LINE\n"
            return placeholder + "\n".join(first_part_lines) + "\n" 

        # Handle indentation issues
        # If the code doesn't start with a block keyword, remove one level of indentation
        for i, line in enumerate(first_part_lines):
            if not line.startswith(" "):
                break
            # Check if the line has no indentation
            if i > 0:
                first_part_lines = [line[4:] if line.startswith("    ") else line for line in first_part_lines]
                break
        print(f"First part lines after processing: {first_part_lines}")
        # Combine the processed first part with the remaining lines
        first_part_str= "\n".join(first_part_lines)
        # remaining_part_str= "\n".join(remaining_lines)
        return first_part_str 

    def fix_incomplete_blocks1(lines):
        """
        Adds placeholders for incomplete blocks.
        """
        
        #if the last line ends with a colon, add a pass statement with one more level of identation
        if lines and lines[-1].strip().endswith(":"):
            #find identation level
            indent = 0
            for char in lines[-1]:
                if char == " ":
                    indent += 1
                else:
                    break

            #if we are currently inside a try block, add a pass statement with the same identation level and an except

            #if we are currently inside an elif block, add a pass statement with the same identation level and an else

            # rest of the cases           
            return lines + [" " * (indent + 4) + "pass  # ADDED_LINE"]
            
    def fix_incomplete_blocks(lines):
        """
        Adds placeholders for incomplete blocks based on the last line or incomplete context.
        Handles cases like missing `else` after `elif` and `except` after `try`.
        """
        if not lines:
            return lines

        # Determine the indentation level of the last line
        def get_indent(line):
            indent = 0
            for char in line:
                if char == " ":
                    indent += 1
                else:
                    break
            return indent



        if lines[-1].strip().endswith(":"):
            # Determine the indentation level of the last line
            line_indent = get_indent(lines[-1])

            # Check the context of the incomplete block
            last_line = lines[-1].strip()
            if last_line.startswith("try:"):
               #retrun the lines without the try:
                lines =lines[:-1]
                lines.append( " " * (line_indent) + "pass # ADDED_LINE")
            elif last_line.startswith("elif "):
                # Add pass and else block
                lines.concat([
                    " " * (line_indent + 4) + "pass # ADDED_LINE",
                    " " * line_indent + "else:",
                    " " * (line_indent + 4) + "pass # ADDED_LINE",
                ])
                
            elif last_line.startswith("else:"):
                # Add pass for else block
                lines.append( " " * (line_indent + 4) + "pass # ADDED_LINE")
            elif last_line.startswith("except"):
                # Add pass for except block
                lines.append(" " * (line_indent + 4) + "pass # ADDED_LINE")
            else:
                # General case: add a pass statement for any other block
                lines.append(" " * (line_indent + 4) + "pass # ADDED_LINE")
            return lines
        # Find all `try` blocks and ensure they are closed with an `except`
        try_positions = [i for i, line in enumerate(lines) if line.strip().startswith("try:")]

        if len(try_positions) > 0:
            try_pos = try_positions[-1]
            try_indent = get_indent(lines[try_pos])
            has_except_or_finally = False

            # Check if there's an `except` or `finally` block after this `try`
            for line in lines[try_pos + 1:]:
                line_indent = get_indent(line)
                if line_indent <= try_indent:
                    # Block ended without an `except` or `finally`
                    break
                if line.strip().startswith(("except", "finally")):
                    has_except_or_finally = True
                    break

            # If no `except` or `finally` found, add them
            if not has_except_or_finally:
                lines.append(" " * try_indent + "except Exception as e: # ADDED_LINE")
                lines.append(" " * (try_indent + 4) + "pass # ADDED_LINE")

        # Check for `elif` blocks and ensure they have an `else`
        elif_positions = [i for i, line in enumerate(lines) if line.strip().startswith("elif:")]
        if len(elif_positions) > 0:
            elif_pos = elif_positions[-1]
            elif_indent = get_indent(lines[elif_pos])
            has_else = False

            # Check if there's an else after the elif
            for line in lines[elif_pos + 1:]:
                line_indent = get_indent(line)
                if line_indent <= elif_indent:
                    # Block ended without an else
                    break
                if line.strip().startswith("else"):
                    has_else = True
                    break

            # If no `except` or `finally` found, add them
            if not has_else:
                lines.append( " " * elif_indent + "else: # ADDED_LINE")
                lines.append( " " * (elif_indent + 4) + "pass # ADDED_LINE")


        return lines



        # fixed_lines = []
        # for line in lines:
        #     fixed_lines.append(line)
        #     if line.strip().endswith(":"):
        #         fixed_lines.append("    pass")
        # return fixed_lines

    def handle_start(snippet_lines):
        """
        Handle the start of the snippet to identify and wrap global code or check functions.
        """
        first_part_lines = []
        in_function = False

        for line in snippet_lines:
            if line.lstrip().startswith("def "):
                in_function = True
            if in_function:
                break
            first_part_lines.append(line)

        remaining_lines = snippet_lines[len(first_part_lines):]
        print(f"First part lines: {first_part_lines}")
        beginning =detect_global_or_function_start(first_part_lines)
        print(f"Beginning: {beginning}")
        if len(first_part_lines) == 0:
            return remaining_lines
        if beginning == "global_start":
            print("Global code detected.")
            print(f"First part lines: {first_part_lines}")
            # if the first part contains a return statement , wrap it into a function
            if any("return" in line for line in first_part_lines):
                process_first_part_unwrapped(first_part_lines)
                print(f"First part lines after processing: {first_part_lines}")
                return wrap_global_code(first_part_lines)+ remaining_lines
            return process_first_part(first_part_lines, remaining_lines)
        elif beginning == "function_start":
            return first_part_lines + remaining_lines
        return wrap_global_code(first_part_lines) + remaining_lines

    def handle_end(lines):
        """
        Handle the end of the snippet by ensuring no incomplete function or block endings.
        """
        if not lines:
            return lines

        last_line = lines[-1].strip()
        if last_line.endswith(":"):
            lines.append("    pass")
        return lines

    # Step 1: Split into lines and trim empty lines and comments
    lines = snippet.splitlines()
    trimmed_lines, imports_str = trim_empty_comments_and_imports(lines)
    print(f"Trimmed lines: {trimmed_lines}")
    # Step 2: Handle the start of the snippet
    snippet_lines = handle_start(trimmed_lines)
    print(f"Snippet lines after handle start: {snippet_lines}")
    #if split_lines is list
    if isinstance(snippet_lines, str):
        snippet_lines = snippet_lines.splitlines()
    # Step 3: Fix incomplete blocks throughout the snippet
    snippet_lines = fix_incomplete_blocks(snippet_lines)
    print(f"Snippet lines after fix incomplete blocks: {snippet_lines}")

    # Step 4: Handle the end of the snippet
    snippet_lines = handle_end(snippet_lines)

    print(f"Snippet lines after handle end: {snippet_lines}")
    if imports_str != "":
        return imports_str +"\n" +"\n".join(snippet_lines)
    return "\n".join(snippet_lines)

def visit(script, node):
    # Check if this node corresponds to an added line
    if hasattr(node, "lineno"):
        line = script.splitlines()[node.lineno - 1].strip()
        if line.endswith("# ADDED_LINE"):
            node.is_added = True  # Mark this node as added
        else:
            node.is_added = False
    visit(script,node)
    return node



"""
Parse the snippet into an AST and mark nodes that were added.
Added lines are identified by a specific marker (e.g., `# ADDED_LINE`).
"""
def mark_node(node, lines):
    """
    Mark the node as added or original based on the source line.
    """
    if hasattr(node, "lineno"):
        line = lines[node.lineno - 1].strip()
        node.is_added = line.endswith("# ADDED_LINE")
    return node

def traverse_and_mark(tree, lines):
    """
    Recursively traverse the AST and mark nodes.
    """
    for node in ast.walk(tree):
        mark_node(node, lines)
    return tree

#read from a file and test the file contents
def test():
    #read file path as argument
    if len(sys.argv) < 2:
        print("Please provide a file path as argument.")
        return
    file_path = sys.argv[1]

    with open(file_path) as file:
        snippet = file.read()
        try:
            ast.parse(snippet)
            print("The snippet was originally parsable.")
        except SyntaxError as e:
            print("The snippet was originally not parsable.")
            snippet= ensure_parsable_program(snippet)
        
        try:
            tree = ast.parse(snippet)
            lines = snippet.splitlines()
            traverse_and_mark(tree, lines)
            for node in ast.walk(tree):
                if hasattr(node, "is_added"):
                    status = "Added" if node.is_added else "Original"
                    print(f"Node: {ast.dump(node)}, Status: {status}")
            print("The snippet was made parsable.")
        except SyntaxError as e:
            print("The snippet was not made parsable.")
        
        print(snippet)

def remove_added_lines(original_with_comments, annotated_version):
    """
    Remove added lines (indicated by # ADDED LINE) from the annotated version of the code
    by matching the corresponding code lines in the annotated version.

    Args:
    - original_with_comments (str): Code with comments indicating added lines.
    - annotated_version (str): Annotated version of the code with added states.

    Returns:
    - str: Annotated version with the added lines removed.
    """
    # Split the code into lines
    original_lines = original_with_comments.splitlines()
    annotated_lines = annotated_version.splitlines()
    #remove empty lines from both code
    original_lines = [line for line in original_lines if line.strip()]
    annotated_lines = [line for line in annotated_lines if line.strip()]

    # Step 1: Identify added lines in the original
    start_index = 0
    for line in original_lines:
        print(line)
        if "# ADDED LINE" in  line.strip():
            start_index += 1
        else:
           
            break

    end_index = len(original_lines)
    for line in reversed(original_lines):
        if "# ADDED LINE" in line.strip():
            end_index -= 1
        else:
            break

    # Step 2: Extract code lines at the identified indexes
    added_start_line = original_lines[start_index - 1].split("# ADDED LINE")[0].rstrip() if start_index > 0 else None
    added_end_line = original_lines[end_index].split("# ADDED LINE")[0].rstrip() if end_index < len(original_lines) else None
    
   
    # Step 3: Find the corresponding indexes in the annotated version
    annotated_start_index=0
    if  added_start_line is not None:
        for i, line in enumerate(annotated_lines, start=1):  # Use start=1 for 1-based indexing
            if line.strip() == added_start_line.strip():
                annotated_start_index = i  # Found the line number
                break 
    print(f"Annotated start index: {annotated_start_index}")
    annotated_end_index = len(annotated_lines)
    if  added_end_line is not None:
        for i, line in enumerate(reversed(annotated_lines), start=1):  # Enumerate reversed lines
            if line.strip() == added_end_line.strip():
                annotated_end_index = len(annotated_lines) - i + 1  # Convert reversed index to normal index
                break  # Exit the loop once a match is found

       
    # Step 4: Remove lines before and after the identified indexes
    filtered_annotated_lines = annotated_lines[annotated_start_index:annotated_end_index]

    # Join the remaining lines back into a single string
    return "\n".join(filtered_annotated_lines)


def run_tests(test_cases_file, config, log_directory, model, test_ids=[]):
    """Run the testing framework."""
    # Load test cases
    total_correct = 0
    total=0
    data = load_test_cases(test_cases_file)
    results = []
    test_cases = data["test_cases"]

    if test_ids:
        test_cases = [case for case in test_cases if case["id"] in test_ids]
        if not test_cases:
            print("No matching test cases found for the provided IDs.")
            return


    for case in test_cases:
        total += 1
        precondition = case["precondition"]
        code = case["code"]
        expected_postcondition = case["expected_postcondition"]
        id = case["id"]

        #create log_directory in the log directory with the id
        log_directory_temp = log_directory / id
        log_directory_temp.mkdir(parents=True, exist_ok=True)
        print(f"Running test case {id}")
        # Get the HoarePrompt postcondition
        hoareprompt_output = compute_postcondition(precondition, code, config, log_directory_temp)

        # Compare postconditions using the LLM
        response, reason = assess_postcondition_equivalence(expected_postcondition, hoareprompt_output, model)
        if response:
            total_correct += 1
            
        print(f"Total correct so far: {total_correct}/{total}")
        # Save the result for this test case
        results.append({
            "id": id,
            "precondition": precondition,
            "code": code,
            "expected_postcondition": expected_postcondition,
            "hoareprompt_postcondition": hoareprompt_output,
            "is_equivalent": response,
            "reason": reason
        })

    results.append({
        "total_correct": total_correct,
        "total": total
    })
    print(f"Total correct: {total_correct}/{total}")
    # Save results to a file
    with (log_directory / 'regression_entailement.json').open("w", encoding="utf-8") as f:
            json.dump(results, f, indent=4)


# def remove_imports_and_comments(script: str) -> tuple:
#     # Extract import statements
#     imports = re.findall(r'^\s*(import .+|from .+ import .+)', script, flags=re.MULTILINE)
#     imports_str = "\n".join(imports)
    
#     # Remove import statements from the script
#     script_no_imports = re.sub(r'^\s*import .*\n?|^\s*from .*\n?', '', script, flags=re.MULTILINE)
    
#     # Remove single-line comments
#     script_no_comments = re.sub(r'#.*', '', script_no_imports)
    
#     # Remove multi-line comments (both """ ... """ and ''' ... ''')
#     script_cleaned = re.sub(r'(""".*?"""|\'\'\'.*?\'\'\')', '', script_no_comments, flags=re.DOTALL)
    
    
#     function_pattern = re.compile(r'\bdef\s+(\w+)\s*\([^)]*\)\s*(->\s*[\w\[\], ]+)?\s*:')

#     function_names = function_pattern.findall(script_cleaned)
#     name_mapping = {name: f'func_{i+1}' for i, name in enumerate(function_names)}
    
#     # Replace each function name in the script with its generic name
#     for original_name, generic_name in name_mapping.items():
#         script_cleaned = re.sub(rf'\b{original_name}\b', generic_name, script_cleaned)


#     return script_cleaned.strip(), imports_str.strip()

def remove_functionality(tree: str) -> str:
    # Define the marker line after which we want to replace content
    marker = "#Overall this is what the function does:"
    
    # Find the position of the marker in the tree
    marker_pos = tree.find(marker)
    
    # If the marker is not found, return the original tree without modifications
    if marker_pos == -1:
        return tree
    
    # Extract the part of the tree up to (and including) the marker
    before_marker = tree[:marker_pos ]
    
    # Combine the content before the marker with the new functionality
   
    return before_marker

def find_function_definition(func_str: str) -> str:
    """
    Extracts the function definition (header) from a string representing a Python function,
    including everything up to the first newline after 'def'.
    
    Args:
        func_str (str): A string containing the Python function.
    
    Returns:
        str: The function definition (header), or an empty string if not found.
    """
    # Match the first "def" keyword to the first newline
    pattern = r"^\s*def.*?:\s*(#.*)?$"
    match = re.search(pattern, func_str, re.MULTILINE)
    if match:
        return match.group().strip()
    return ""


def remove_imports_and_comments(script: str) -> tuple:
    # Parse the script into an AST
    tree = ast.parse(script)

    # Initialize storage for import statements and function name mapping
    imports = []
    function_names = []
    function_mapping = {}
    added_lines = []

    
    lines = script.splitlines()

    # Separate imports from global code and collect function names
    filtered_body = []
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            # Collect the import statements separately
            imports.append(ast.get_source_segment(script, node))
        else:
            # Keep non-import nodes in the body for global code processing
            filtered_body.append(node)
            # Collect function names
            if isinstance(node, ast.FunctionDef):
                function_names.append(node.name)

    # Update the tree with non-import nodes only
    tree.body = filtered_body

    # Generate a name mapping for generic function names
    function_mapping = {name: f'func_{i + 1}' for i, name in enumerate(function_names)}

    # Custom NodeTransformer to replace function names
    class FunctionRenamer(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            # Rename the function in the definition
            if node.name in function_mapping:
                node.name = function_mapping[node.name]
            self.generic_visit(node)
            return node

        def visit_Call(self, node):
            # Rename function in function calls
            if isinstance(node.func, ast.Name) and node.func.id in function_mapping:
                node.func.id = function_mapping[node.func.id]
            self.generic_visit(node)
            return node

    # Apply renaming transformation
    renamer = FunctionRenamer()
    tree = renamer.visit(tree)
    ast.fix_missing_locations(tree)

    for line in lines:
        stripped = line.strip()
        if "#" in stripped and stripped.endswith("# ADDED LINE"):
            # Store the full line without the '# ADDED LINE' comment
            added_lines.append(stripped.replace("# ADDED LINE", "").strip())

        # Generate cleaned script from the AST
        cleaned_script_from_ast = ast.unparse(tree)

        # Add '# ADDED LINE' back to the cleaned script for matching lines
        cleaned_lines = cleaned_script_from_ast.splitlines()
        updated_cleaned_lines = []

        for line in cleaned_lines:
            stripped_line = line.strip()
            if stripped_line in added_lines:
                updated_cleaned_lines.append(line + "  # ADDED LINE")
            else:
                updated_cleaned_lines.append(line)

        # Join the lines back into a single string
        cleaned_script_with_added_lines = "\n".join(updated_cleaned_lines)
    

    # Join imports as a separate string
    imports_str = "\n".join(imports)

    return cleaned_script_with_added_lines.strip(), imports_str.strip()

# def extract_functions(script: str) -> dict:
#     # Initialize storage for functions and global code
#     functions = []
#     global_code = ""
#     function_pattern = re.compile(r'\bdef\s+(\w+)\s*\([^)]*\)\s*(->\s*[\w\[\], ]+)?\s*:', re.MULTILINE)

#     # Recursively extract functions until no more matches are found
#     while True:
#         matches = list(function_pattern.finditer(script))
        
#         # If no functions are found, break the loop
#         if not matches:
#             break

#         # Process matches in reverse order to handle nested functions correctly
#         for match in reversed(matches):
#             func_indent = len(match.group(1))  # Indentation level of this function
#             func_start = match.start()
#             func_line_num = script[:func_start].count("\n")
            
#             # Split the script into lines for easier processing
#             remaining_script = script.splitlines()
            
#             # Start collecting function body
#             func_body = []
#             func_body.append(remaining_script[func_line_num])

#             # Gather all indented lines that belong to this function
#             for i in range(func_line_num + 1, len(remaining_script)):
#                 line = remaining_script[i]
#                 line_indent = len(line) - len(line.lstrip())
                
#                 if line_indent > func_indent:
#                     func_body.append(line)
#                 else:
#                     #if the line is not empty
#                     if not line.strip():
#                         break

#             # Add the captured function, stripping any excess indentation
#             functions.append(dedent("\n".join(func_body)))

#             # Remove the processed function from the script
#             script_lines = script.splitlines()
#             del script_lines[func_line_num:func_line_num + len(func_body)]
#             script = "\n".join(script_lines)

#     # Any remaining script after function extraction is considered global code
#     global_code = script.strip()

#     # If no functions were found initially, wrap everything in a dummy function
#     if not functions:
#         dummy_function = "def func():\n    " + "\n    ".join(global_code.splitlines())
#         functions.append(dummy_function)
#         global_code = ""

#     return {"global_code": global_code, "functions":  functions[::-1]}


def extract_functions_v2(script: str) -> dict:
    """
    Extracts functions and global code from a Python script while preserving comments like `# ADDED LINE`.
    """
    # Parse the script into an AST
    tree = ast.parse(script)
    functions = []
    global_code_lines = []
    script_lines = script.splitlines()

    # Recursive function to capture functions, including nested ones, and strip nested code
    def capture_functions(node, lines):
        if isinstance(node, ast.FunctionDef):
            # Get the source lines for this function
            func_start_line = node.lineno - 1  # Adjust for 1-based indexing
            func_end_line = node.end_lineno    # End line provided by AST
            function_source = lines[func_start_line:func_end_line]

            # Strip out nested function lines within the outer function
            nested_function_lines = set()
            for child in ast.walk(node):
                if isinstance(child, ast.FunctionDef) and child != node:
                    nested_start = child.lineno - 1
                    nested_end = child.end_lineno
                    for i in range(nested_start, nested_end):
                        nested_function_lines.add(i)

            # Remove nested function lines from the outer function, preserving comments
            function_body = [
                line for i, line in enumerate(function_source)
                if func_start_line + i not in nested_function_lines
            ]
            functions.append("\n".join(function_body))
        
        # Recur through child nodes to capture nested functions
        for child in ast.iter_child_nodes(node):
            capture_functions(child, lines)
    
    # Manually process global code to preserve comments
    function_ranges = [
        (node.lineno - 1, node.end_lineno) for node in tree.body if isinstance(node, ast.FunctionDef)
    ]
    covered_lines = set()
    for start, end in function_ranges:
        covered_lines.update(range(start, end))
    
    # Lines not covered by functions are considered global code
    for i, line in enumerate(script_lines):
        if i not in covered_lines:
            global_code_lines.append(line)
    
    # Capture functions from the AST
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            capture_functions(node, script_lines)
    
    # Join the remaining lines as global code
    global_code = "\n".join(global_code_lines).strip()

    # If no functions are found, wrap the entire code in a dummy function
    if not functions:
        dummy_function = "def func():\n    " + "\n    ".join(global_code.splitlines())
        functions = [dummy_function]
        global_code = ""

    return {"global_code": global_code, "functions": functions}

def extract_functions(script: str) -> dict:
    # Parse the script into an AST
    tree = ast.parse(script)
    functions = []
    global_code_lines = []

    # Recursive function to capture functions, including nested ones, and strip nested code
    def capture_functions(node, lines):
        if isinstance(node, ast.FunctionDef):
            # Get the source lines for this function
            func_start_line = node.lineno - 1  # Adjust for 1-based indexing
            func_end_line = node.end_lineno    # End line provided by AST
            function_source = lines[func_start_line:func_end_line]

            # Strip out nested function lines within the outer function
            nested_function_lines = set()
            for child in ast.walk(node):
                if isinstance(child, ast.FunctionDef) and child != node:
                    nested_start = child.lineno - 1
                    nested_end = child.end_lineno
                    for i in range(nested_start, nested_end):
                        nested_function_lines.add(i)

            # Remove nested function lines from the outer function
            function_body = [line for i, line in enumerate(function_source) if func_start_line + i not in nested_function_lines]
            functions.append(dedent("\n".join(function_body)))
        
        # Recur through child nodes to capture nested functions
        for child in ast.iter_child_nodes(node):
            capture_functions(child, lines)
    
    # Capture functions and non-function global code
    script_lines = script.splitlines()
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            capture_functions(node, script_lines)
        else:
            # Collect lines for non-function nodes as global code
            global_code_lines.extend(ast.get_source_segment(script, node).splitlines())
    
    # Join the remaining lines as global code
    global_code = "\n".join(global_code_lines).strip()

    # If no functions are found, wrap the entire code in a dummy function
    if not functions:
        dummy_function = "def func():\n    " + "\n    ".join(global_code.splitlines())
        functions = [dummy_function]
        global_code = ""

    return {"global_code": global_code, "functions": functions}

def main():
    # Initialize argument parser with description of the tool

    parser = argparse.ArgumentParser(description="HoarePrompt: Structural Reasoning About Programs in Natural Language")
    
    # Add common options for configuration and log directory
    parser.add_argument('--config', type=str, help="Path to custom configuration file")
    parser.add_argument('--log', type=str, help="Directory to save detailed logs")

    # Add the --command argument, which can be 'assess', 'extract-precondition', 'compute-postcondition', or 'check-entailment'
    parser.add_argument('--command', type=str, choices=['assess', 'extract-precondition', 'compute-postcondition', 'check-entailment'], help="Specify the command to run")
    

    # Arguments that could be used in different commands
    parser.add_argument('--description', type=str, help="Path to the description file")
    parser.add_argument('--program',  type=str, help="Path to the program file")
    parser.add_argument('--precondition', type=str, help="Path to the precondition file")
    parser.add_argument('--postcondition', type=str, help="Path to the postcondition file")
    parser.add_argument('--cex', type=str, help="Output file for the counterexample")
    
    parser.add_argument('--test', nargs='*', help="Run in test mode using pre-defined test cases. Optionally, provide test IDs.")
    # Parse the command-line arguments
    args = parser.parse_args()
    # If no commnad is provided assume assess

    

    if not args.command:
        print("No command provided, defaulting to 'assess'")
        args.command = 'assess'

    # Load the configuration file if provided, otherwise use a default configuration
    if args.config:
        config_file = Path(args.config)
    else:
        config_file = Path("default_config.json")

    with config_file.open() as f:
        config = json.load(f)

    if "confidence" not in config:
        config["confidence"] = False

    if "incomplete" not in config:
        config["incomplete"] = False
    
    if "completion_mode" not in config:
        config["completion_mode"] = "llm"

    
    #if config annotated is true and  config  "assessment-mode": "naive" print error thaty they are noit compatible and that annotated only with postcondition-entailment
    if "annotated"  in config:
        if config["annotated"] and config["assessment-mode"] == "naive":
            print("Error: Annotated mode is only compatible with 'postcondition-entailment' assessment mode")
            return
        if config["annotated"] and config["assessment-mode"] == "single-postcondition":
            print("Error: Annotated mode is only compatible with 'postcondition-entailment' assessment mode")
            return
        if config["annotated"] and config["assessment-mode"] == "single-postcondition-no-fsl":
            print("Error: Annotated mode is only compatible with 'postcondition-entailment' assessment mode")
            return
        if config["annotated"] :
            if "annotated-type" not in config:
                print("Annotated mode need annotated-type to be defined, defaulting to complex")
                config["annotated-type"] = "complex"
            
    else :
        config["annotated"] = False
    #if in the configuration we have the config option fsl and we have it set to true
    #first check if the fsl option exists in config
    if "fsl" in config:
        if not config["fsl"]:
            #if fsl is set to true then we have to check if the assessment mode is set to postcondition-entailment
            if config["annotated"] == True:
                print("Error: FSL mode as False  is only compatible when annotated is false")
                return
    else:
        #if the fsl option does not exist in the config file then we have to set it to false
        config["fsl"] = True
    # Setup log directory if provided
    # If it is not provided, create the log_temporary directory
    # If the log directory already exists, delete it and recreate it

    if config["confidence"] and config["assessment-mode"] != "naive":
        print("Error: Confidence is only compatible with 'naive' assessment mode")
        return
    if config["confidence"] and config["assessment-mode"] == "naive":
        if config["fsl"]:
            print("Error: Confidence is not compatible with FSL true")
            return
        

    log_directory = None
    if args.log:
        log_directory = Path(args.log)
    else:
        log_directory = Path("log_temporary")

    # If the log directory exists, delete it and recreate
    if log_directory.exists():
        shutil.rmtree(log_directory)

    # Create the log directory
    log_directory.mkdir(parents=True, exist_ok=True)

    # I also want to store the config file in the log directory so that we know what configuration were used for each run
    with (log_directory / 'config.json').open("w") as f:
        json.dump(config, f, indent=4)


    cex_path = None

    if args.test is not None:
        # Get the model for testing
        model = get_model("gpt-4o-2024-08-06", config["temperature"], log_directory)
        print("Running in test mode")
        
        # Check for regression_test_cases.json file
        if Path("regression_test_cases.json").exists():
            filename = "regression_test_cases.json"
        else:
            filename = "src/regression_test_cases.json"

        # If specific test IDs are provided, use them; otherwise, run all tests
        test_ids = args.test if args.test else []
        print(f"Test IDs to run: {test_ids}" if test_ids else "Running all tests")
        
        # Run tests with the provided IDs
        run_tests(filename, config, log_directory, model, test_ids)
        exit(0)
    else:
        if not args.program:
            print("Error: No program file provided")
            exit(1)

    # Handle the 'assess' command
    if args.command == 'assess':

         # Ensure required arguments for the 'assess' command are provided
        if not args.description or not args.program:
            raise ValueError("Both --description and --program must be provided for the 'assess' command.")
        
        # Read the description and program files
        with open(args.description, 'r') as f:
            description = f.read()
        with open(args.program, 'r') as f:
            program = f.read()
        # Get the module name from the program file name
        module_name = os.path.splitext(os.path.basename(args.program))[0]

        if config["incomplete"]:
            print("Using incomplete mode to get missing code")
            complete_incomplete(description, program, module_name, config, log_directory)
        else:
            
            # Set the path for the counterexample file if provided
            if args.cex:
                cex_path = Path(args.cex)
            assess(description, program, module_name, config, log_directory, cex_path)
    
    # Handle the 'extract-precondition' command
    elif args.command == 'extract-precondition':
        if not args.description or not args.program:
            raise ValueError("Both --description and --program must be provided for the 'extract-precondition' command.")
        
        with open(args.description, 'r') as f:
            description = f.read()
        with open(args.program, 'r') as f:
            program = f.read()
        
        # Get the module name from the program file name
        module_name = os.path.splitext(os.path.basename(args.program))[0]

        # Save the program and description to the log directory
        with (log_directory / str(module_name + '.py')).open("w", encoding="utf-8") as f:
            f.write(program)
        with (log_directory / 'description.txt').open("w", encoding="utf-8") as f:
            f.write(description)

        # Extract the precondition from the description and program
        precondition_log_dir = log_directory / 'extract-precondition'
        precondition_log_dir.mkdir()
        precondition = extract_precondition(description, program, config, precondition_log_dir)
        
        # Save the extracted precondition
        with (log_directory / 'precondition.txt').open("w", encoding="utf-8") as f:
            f.write(precondition)
        return precondition
    
    # Handle the 'compute-postcondition' command
    elif args.command == 'compute-postcondition':
        if not args.precondition or not args.program:
            raise ValueError("Both --precondition and --program must be provided for the 'compute-postcondition' command.")
        with open(args.precondition, 'r') as f:
            precondition = f.read()
        with open(args.program, 'r') as f:
            program = f.read()
        
        module_name = os.path.splitext(os.path.basename(args.program))[0]

        # Save the program and description to the log directory
        with (log_directory / str(module_name + '.py')).open("w", encoding="utf-8") as f:
            f.write(program)
        with (log_directory / 'precondition.txt').open("w", encoding="utf-8") as f:
            f.write(precondition)
        
        postcondition_log_dir = log_directory / 'compute-postcondition'
        postcondition_log_dir.mkdir()
        postcondition = compute_postcondition(precondition, program, config, postcondition_log_dir)

        # Save the computed postcondition
        with (log_directory / 'postcondition.txt').open("w", encoding="utf-8") as f:
            f.write(postcondition)

        return postcondition
    # Handle the 'check-entailment' command
    elif args.command == 'check-entailment':
        if not args.description or not args.program or not args.postcondition:
            raise ValueError("Both --description, --program, and --postcondition must be provided for the 'check-entailment' command.")
        with open(args.description, 'r') as f:
            description = f.read()
        with open(args.postcondition, 'r') as f:
            postcondition = f.read()
        with open(args.program, 'r') as f:
            program = f.read()
        # Get the module name and set counterexample path if provided
        module_name = os.path.splitext(os.path.basename(args.program))[0]
        if args.cex:
            cex_path = Path(args.cex)
            
        
        with (log_directory / 'description.txt').open("w", encoding="utf-8") as f:
            f.write(description)
        with (log_directory / 'postcondition.txt').open("w", encoding="utf-8") as f:
            f.write(postcondition)
        with (log_directory / str(module_name + '.py')).open("w", encoding="utf-8") as f:
            f.write(program)
        
        

        # Check entailment to verify consistency with the description
        entailment_log_dir = log_directory / 'check_entailment'
        entailment_log_dir.mkdir()

        result= check_entailment(description, postcondition, program, module_name, config, log_directory, cex_path)
        # Print result (CORRECT or INCORRECT) and log counterexample if provided
        if result:
            print('CORRECT')
        else:
            print('INCORRECT')
        
        if cex_path:
            with open(cex_path, 'r') as f:
                cex_code = f.read()
            with (log_directory / os.path.basename(cex_path)).open("w", encoding="utf-8") as f:
                f.write(cex_code)
            
    # If no command is provided, display help information
    else:
        parser.print_help()



def complete_incomplete(description, program, module_name, config, log_directory):
    if config["completion_mode"] == "llm":
        print("Using LLM completion mode to get missing code")
        completion_log_dir = log_directory / 'completion_llm'
        completion_log_dir.mkdir(parents=True, exist_ok=True)
        model = get_model(config["model"], config["temperature"], completion_log_dir)
        completed_code= code_completor.default(model, description, program)
        assess_incomplete(description, completed_code, module_name, config, log_directory)
    else:
        snippet=program
        try:
            ast.parse(snippet)
            print("The snippet was originally parsable.")
        except SyntaxError as e:
            print("The snippet was originally not parsable.")
            snippet= ensure_parsable_program(snippet)
        
        try:
            tree = ast.parse(snippet)
            lines = snippet.splitlines()
            traverse_and_mark(tree, lines)
            for node in ast.walk(tree):
                if hasattr(node, "is_added"):
                    status = "Added" if node.is_added else "Original"
                    print(f"Node: {ast.dump(node)}, Status: {status}")
            print("The snippet was made parsable.")
            print(snippet)
        except SyntaxError as e:
            print("The snippet was not made parsable.")
            #throw error

        incomplete_precondition_dir = log_directory / 'incomplete_precondition'
        incomplete_precondition_dir.mkdir(parents=True, exist_ok=True)
        model = get_model(config["model"], config["temperature"], incomplete_precondition_dir)
        incomplete_precondition = precondition_extractor_incomplete.default(model, description, snippet.replace("# ADDED LINE", ""))
        assess_incomplete(description, snippet, module_name, config, log_directory, llm_precondition= incomplete_precondition)

        
        

# Assess if a program is consistent with the description using pre/postconditions and entailment checking
def assess_incomplete(description, program, module_name, config, log_directory, llm_precondition= "", cex_path=None):
    print(f"the program is\n{program}\n")
    cleaned_program, imports = remove_imports_and_comments(program)
    print(f"the cleaned program is\n{cleaned_program}\n")
    functions_dict = extract_functions_v2(cleaned_program)
    # print("this is the functions dict", functions_dict)
    functions_list_with_comment= functions_dict["functions"]
    print(f"functions list with comment is\n{functions_list_with_comment}\n")
    global_code = functions_dict["global_code"]
    postconditions_list =[]
    return_list=[]
    annotated_func_list = []
    remade_program = ""
    functions_list = []
    #remake the program with the functions
    if imports != "":
        remade_program += imports + "\n\n"
    if global_code != "":
        remade_program += global_code + "\n\n"
    for func in functions_list_with_comment:
        functions_list.append(func.replace("# ADDED LINE", "").strip())
        remade_program += func + "\n\n"

    first_original_line = None
    #find the first line without the added line ,thats no a function def
    for func in functions_list_with_comment:
        if "# ADDED LINE" in func:
            for line in func.splitlines():
                if not "# ADDED LINE" in line.strip() and not line.strip().startswith("def"):
                    first_original_line = line.strip()
                    break
    # For the first function, add a '# ADDED LINE' to the function definition
    if functions_list_with_comment[0].splitlines()[0].startswith("def"):
        lines = functions_list_with_comment[0].splitlines()  # Split into lines
        lines[0] += " # ADDED LINE"  # Add the comment to the first line
        functions_list_with_comment[0] = "\n".join(lines)  # Rejoin lines into a single string
    print(f"functions list with comment is\n{functions_list_with_comment}\n")
    print(f"the imports are\n{imports}\n")
    print(f"the global code is\n{global_code}\n")
    for index, func in enumerate(functions_list):
        print(f"Function {index} is: \n{func}\n ")
    
    if config['assessment-mode'] == 'naive':
        print("Using naive assessment mode")
        return compute_postcondition_naive(description, remade_program, config, log_directory)
    
    if config['assessment-mode'] == 'single-postcondition' or config['assessment-mode'] == 'single-postcondition-no-fsl':
        print(f"Using {config['assessment-mode']} assessment mode")
        return compute_postcondition_single(description, functions_list,imports, global_code, cleaned_program, module_name, program, config, log_directory)
    # Ensure assessment mode is set to 'postcondition-entailment'
    assert config['assessment-mode'] in {'postcondition-entailment', 'total', 'verify'}

    
    # Save the program and description to the log directory
    with (log_directory / str(module_name + '.py')).open("w", encoding="utf-8") as f:
        f.write(program)
    with (log_directory / str(module_name + '_cleaned.py')).open("w", encoding="utf-8") as f:
        f.write(cleaned_program)
    with (log_directory / 'description.txt').open("w", encoding="utf-8") as f:
        f.write(description)
    
    precondition_log_dir = log_directory / 'extract-precondition'
    precondition_log_dir.mkdir(parents=True, exist_ok=True)

    postcondition_log_dir = log_directory / 'compute-postcondition'
    postcondition_log_dir.mkdir(parents=True, exist_ok=True)
    
    for index, func in enumerate(functions_list):
        # Extract the precondition from the description and program
        func_withcomments =functions_list_with_comment[index]
        

        if llm_precondition != "" and index == 0:
            precondition = llm_precondition
        else:
            precondition = extract_precondition(description, func, config, precondition_log_dir,len(functions_list))
        
        # Save the extracted precondition
        with (log_directory / f'precondition_func_{index}.txt').open("w", encoding="utf-8") as f:
            f.write(precondition)

        # Compute the postcondition from the precondition and program
        # This is where the important work gets done
        postcondition_total =compute_postcondition(precondition, func, config, postcondition_log_dir, first_original_line)
        if len(postcondition_total) == 4:
            postcondition = postcondition_total[0]
            return_str = postcondition_total[1]
            annotated_func = postcondition_total[2]
            precondition_selected = postcondition_total[3]
            print(f"the annotated function is\n{annotated_func}\n")
            print(f"the func with comments is\n{func_withcomments}\n")
            annotated_func =remove_added_lines(func_withcomments, annotated_func)
            annotated_func = f"#{precondition_selected} \n {annotated_func}"
            print(f"the new annotated function is\n{annotated_func}\n")
            postconditions_list.append(postcondition)
            return_list.append(return_str)
            annotated_func_list.append(annotated_func)
        elif len(postcondition_total) == 3:
            postcondition = postcondition_total[0]
            return_str = postcondition_total[1]
            annotated_func = postcondition_total[2]
            print(f"the annotated function is\n{annotated_func}\n")
            print(f"the func with comments is\n{func_withcomments}\n")
            annotated_func =remove_added_lines(func_withcomments, annotated_func)
            print(f"the new annotated function is\n{annotated_func}\n")
            postconditions_list.append(postcondition)
            return_list.append(return_str)
            annotated_func_list.append(annotated_func)
        else:
            postcondition = postcondition_total
            postconditions_list.append(postcondition)
        
        if len(annotated_func_list) >0:
            with (log_directory / str('annotated_func' + '.py')).open("w", encoding="utf-8") as f:
                for func in annotated_func_list:
                    f.write(func)
                    f.write("\n\n")
        # Save the computed postcondition
        with (log_directory / f'postcondition_func_{index}.txt').open("w", encoding="utf-8") as f:
            f.write(postcondition)

        

    # print(f"the postconditions are\n {postconditions_list}\n")
    # print(f"the return values are\n {return_list}\n")
    # print(f"the annotated functions are\n {annotated_func_list}\n")
    # Check entailment to verify consistency with the description
    entailment_log_dir = log_directory / 'check_entailment'
    entailment_log_dir.mkdir(parents=True, exist_ok=True)

    if config["assessment-mode"] == "total" or config["assessment-mode"] == "verify":
        print("Using total or verify entailment mode")
        entailment_log_dir_simple = entailment_log_dir/'entailment_simple'
        entailment_log_dir_simple.mkdir(parents=True, exist_ok=True)
        entailment_log_dir_complex = entailment_log_dir/'entailment_complex'
        entailment_log_dir_complex.mkdir(parents=True, exist_ok=True)
        entailment_log_dir_default = entailment_log_dir/'entailment_default'
        entailment_log_dir_default.mkdir(parents=True, exist_ok=True)
        entailment_log_dir_simple_verify = entailment_log_dir/'entailment_simple_verify'
        entailment_log_dir_simple_verify.mkdir(parents=True, exist_ok=True)
        entailment_log_dir_complex_verify = entailment_log_dir/'entailment_complex_verify'
        entailment_log_dir_complex_verify.mkdir(parents=True, exist_ok=True)
        entailment_log_dir_default_verify = entailment_log_dir/'entailment_default_verify'
        entailment_log_dir_default_verify.mkdir(parents=True, exist_ok=True)
        entailment_log_dir_default_no_fsl = entailment_log_dir/'entailment_default_no_fsl'
        entailment_log_dir_default_no_fsl.mkdir(parents=True, exist_ok=True)

    if len(postconditions_list)==1:

        if global_code != "":
            annotated_func = global_code + "\n\n" + annotated_func
        
        if imports != "":
            annotated_func = imports + "\n\n" + annotated_func

        if cex_path:
            result = check_entailment(description, postcondition,remade_program, module_name, config, entailment_log_dir, return_str, annotated_func,cex_path )
        else:
            result = check_entailment(description, postcondition, remade_program, module_name, config, entailment_log_dir, return_str, annotated_func)
    else:
        if cex_path:
            result = check_entailment_mult_func(description, postconditions_list, functions_list, imports,global_code, module_name, config, entailment_log_dir, return_list, annotated_func_list,cex_path)
        else:
            result = check_entailment_mult_func(description, postconditions_list, functions_list, imports, global_code, module_name, config, entailment_log_dir, return_list, annotated_func_list)

    
    # Print result (CORRECT or INCORRECT) and log counterexample if provided
    if result:
        print('CORRECT')
    else:
        print('INCORRECT')
        if cex_path:
            with open(cex_path, 'r') as f:
                cex_code = f.read()
            with (log_directory / os.path.basename(cex_path)).open("w", encoding="utf-8") as f:
                f.write(cex_code)
    return result

# Assess if a program is consistent with the description using pre/postconditions and entailment checking
def assess(description, program, module_name, config, log_directory, cex_path):
    
    cleaned_program, imports = remove_imports_and_comments(program)
    
    functions_dict = extract_functions(cleaned_program)
    # print("this is the functions dict", functions_dict)
    functions_list= functions_dict["functions"]
    global_code = functions_dict["global_code"]
    postconditions_list =[]
    return_list=[]
    annotated_func_list = []
    remade_program = ""

    #remake the program with the functions
    if imports != "":
        remade_program += imports + "\n\n"
    if global_code != "":
        remade_program += global_code + "\n\n"
    for func in functions_list:
        remade_program += func + "\n\n"

    
    print(f"the imports are\n{imports}\n")
    print(f"the global code is\n{global_code}\n")
    for index, func in enumerate(functions_list):
        print(f"Function {index} is: \n{func}\n ")
    
    if config['assessment-mode'] == 'naive':
        print("Using naive assessment mode")
        return compute_postcondition_naive(description, remade_program, config, log_directory)
    
    if config['assessment-mode'] == 'single-postcondition' or config['assessment-mode'] == 'single-postcondition-no-fsl':
        print(f"Using {config['assessment-mode']} assessment mode")
        return compute_postcondition_single(description, functions_list,imports, global_code, cleaned_program, module_name, program, config, log_directory)
    # Ensure assessment mode is set to 'postcondition-entailment'
    assert config['assessment-mode'] in {'postcondition-entailment', 'total', 'verify'}

    
    # Save the program and description to the log directory
    with (log_directory / str(module_name + '.py')).open("w", encoding="utf-8") as f:
        f.write(program)
    with (log_directory / str(module_name + '_cleaned.py')).open("w", encoding="utf-8") as f:
        f.write(cleaned_program)
    with (log_directory / 'description.txt').open("w", encoding="utf-8") as f:
        f.write(description)
    
    precondition_log_dir = log_directory / 'extract-precondition'
    precondition_log_dir.mkdir(parents=True, exist_ok=True)

    postcondition_log_dir = log_directory / 'compute-postcondition'
    postcondition_log_dir.mkdir(parents=True, exist_ok=True)
    
    for index, func in enumerate(functions_list):
        # Extract the precondition from the description and program
        
        precondition = extract_precondition(description, func, config, precondition_log_dir,len(functions_list))
        
        # Save the extracted precondition
        with (log_directory / f'precondition_func_{index}.txt').open("w", encoding="utf-8") as f:
            f.write(precondition)

        # Compute the postcondition from the precondition and program
        # This is where the important work gets done
        postcondition_total = compute_postcondition(precondition, func, config, postcondition_log_dir)
        if len(postcondition_total) == 3:
            postcondition = postcondition_total[0]
            return_str = postcondition_total[1]
            annotated_func = postcondition_total[2]
            
            postconditions_list.append(postcondition)
            return_list.append(return_str)
            annotated_func_list.append(annotated_func)
        else:
            postcondition = postcondition_total
            postconditions_list.append(postcondition)
        
        if len(annotated_func_list) >0:
            with (log_directory / str('annotated_func' + '.py')).open("w", encoding="utf-8") as f:
                for func in annotated_func_list:
                    f.write(func)
                    f.write("\n\n")
        # Save the computed postcondition
        with (log_directory / f'postcondition_func_{index}.txt').open("w", encoding="utf-8") as f:
            f.write(postcondition)

        

    # print(f"the postconditions are\n {postconditions_list}\n")
    # print(f"the return values are\n {return_list}\n")
    # print(f"the annotated functions are\n {annotated_func_list}\n")
    # Check entailment to verify consistency with the description
    entailment_log_dir = log_directory / 'check_entailment'
    entailment_log_dir.mkdir(parents=True, exist_ok=True)

    if config["assessment-mode"] == "total" or config["assessment-mode"] == "verify":
        print("Using total or verify entailment mode")
        entailment_log_dir_simple = entailment_log_dir/'entailment_simple'
        entailment_log_dir_simple.mkdir(parents=True, exist_ok=True)
        entailment_log_dir_complex = entailment_log_dir/'entailment_complex'
        entailment_log_dir_complex.mkdir(parents=True, exist_ok=True)
        entailment_log_dir_default = entailment_log_dir/'entailment_default'
        entailment_log_dir_default.mkdir(parents=True, exist_ok=True)
        entailment_log_dir_simple_verify = entailment_log_dir/'entailment_simple_verify'
        entailment_log_dir_simple_verify.mkdir(parents=True, exist_ok=True)
        entailment_log_dir_complex_verify = entailment_log_dir/'entailment_complex_verify'
        entailment_log_dir_complex_verify.mkdir(parents=True, exist_ok=True)
        entailment_log_dir_default_verify = entailment_log_dir/'entailment_default_verify'
        entailment_log_dir_default_verify.mkdir(parents=True, exist_ok=True)
        entailment_log_dir_default_no_fsl = entailment_log_dir/'entailment_default_no_fsl'
        entailment_log_dir_default_no_fsl.mkdir(parents=True, exist_ok=True)

    if len(postconditions_list)==1:

        if global_code != "":
            annotated_func = global_code + "\n\n" + annotated_func
        
        if imports != "":
            annotated_func = imports + "\n\n" + annotated_func

        if cex_path:
            result = check_entailment(description, postcondition,remade_program, module_name, config, entailment_log_dir, return_str, annotated_func,cex_path )
        else:
            result = check_entailment(description, postcondition, remade_program, module_name, config, entailment_log_dir, return_str, annotated_func)
    else:
        if cex_path:
            result = check_entailment_mult_func(description, postconditions_list, functions_list, imports,global_code, module_name, config, entailment_log_dir, return_list, annotated_func_list,cex_path)
        else:
            result = check_entailment_mult_func(description, postconditions_list, functions_list, imports, global_code, module_name, config, entailment_log_dir, return_list, annotated_func_list)

    
    # Print result (CORRECT or INCORRECT) and log counterexample if provided
    if result:
        print('CORRECT')
    else:
        print('INCORRECT')
        if cex_path:
            with open(cex_path, 'r') as f:
                cex_code = f.read()
            with (log_directory / os.path.basename(cex_path)).open("w", encoding="utf-8") as f:
                f.write(cex_code)
    return result
# Extract the precondition from a description and program using a model
def extract_precondition(description, program, config, log_directory, functions_num =1):
    model = get_model(config["model"], config["temperature"], log_directory)
    if functions_num >1:
        return precondition_extractor_multi_func.default(model,description, program)
    else:
        program_def =find_function_definition(program)
        # Use the precondition extractor model to generate the precondition
        return precondition_extractor.default(model, description, program_def)


def compute_postcondition_single(description, functions_list, imports, global_code, cleaned_program, module_name, program, config, log_directory):
    model = get_model(config["model"], config["temperature"], log_directory)
    # Save the program and description to the log directory
    with (log_directory / str(module_name + '.py')).open("w", encoding="utf-8") as f:
        f.write(program)
    with (log_directory / str(module_name + '_cleaned.py')).open("w", encoding="utf-8") as f:
        f.write(cleaned_program)
    with (log_directory / 'description.txt').open("w", encoding="utf-8") as f:
        f.write(description)
    
    precondition_log_dir = log_directory / 'extract-precondition'
    precondition_log_dir.mkdir(parents=True, exist_ok=True)

    postcondition_log_dir = log_directory / 'compute-postcondition'
    postcondition_log_dir.mkdir(parents=True, exist_ok=True)
    all_funcs= ""
    for index, func in enumerate(functions_list):
        # Extract the precondition from the description and program
        
        precondition = extract_precondition(description, func, config, precondition_log_dir, len(functions_list))
        
        # Save the extracted precondition
        with (log_directory / f'precondition_func_{index}.txt').open("w", encoding="utf-8") as f:
            f.write(precondition)

        # Compute the postcondition from the precondition and program
        # This is where the important work gets done
        if config['assessment-mode'] == 'single-postcondition' :
            postcondition_total = single_post(precondition, func, model)
        elif config['assessment-mode'] == 'single-postcondition-no-fsl' :
            postcondition_total = single_post_no_fsl(precondition, func, model)
        else :
            print(f"Error: {config['assessment-mode']} should not have reached this function")
            exit(1)
        
        func_updated =func + "\n" + f"#State after the function execution: {postcondition_total}"
        all_funcs += func_updated + "\n\n"
    all_funcs = imports+"\n" + global_code+"\n"+ all_funcs
    if config["fsl"]:
        response = naive_question(description, all_funcs, model)
    else:
        response = naive_question_no_fsl(description, all_funcs, model)
    return response
            

# if the assessment mode is set to 'naive', use the naive_question function to compute the postcondition
# we just do an llm call to get if the oce is correct or not using the naive_question function from naive.py
# the prompt and the response from the one API call we are performing are stored in the log dir
def compute_postcondition_naive(description, program, config, log_directory):
    model = get_model(config["model"], config["temperature"], log_directory)
    if not config["fsl"]:
        if config["confidence"]:
            print("FSL is set to False, using naive_question_no_fsl_confidence")
            #dont use few shot learning
            # response1, confidence1 = naive_question_no_fsl_confidence(description, program, model)
            # response2, confidence2 = naive_question_no_fsl_confidence_2(description, program, model)
            response, confidence = naive_question_no_fsl_confidence_qwen(description, program, model)
            # print("I am here")
            response = response, confidence
        else:
            print("FSL is set to False, using naive_question_no_fsl")
            #dont use few shot learning
            response = naive_question_no_fsl(description, program, model)
    else:
        response = naive_question(description, program, model)
    
    return response

# Compute the postcondition from a precondition and program
def compute_postcondition(precondition, program, config, log_directory, first_line= None):
    model = get_model(config["model"], config["temperature"], log_directory)

    # Check the mode for postcondition generation and use the appropriate algorithm
    if config['postcondition-mode'] == 'hoarecot':
        sp_algorithms = {
            "comment-style": comment_style.compute_postcondition,
            "node-based-style": node_base_style.complete_incomplete_snippets.compute_postcondition
        }
        # Select and execute the correct strategy
        sp = sp_algorithms[config['postcondition-cot-prompt']]
        
        return sp(model, precondition, program, config, first_line)
    else:
        raise NotImplementedError

# Check if the postcondition implies compliance with the description using entailment
def check_entailment(description, postcondition, program, module_name, config, log_directory, return_str, annotated_func, cex_path=None):
    model = get_model(config["model"], config["temperature"], log_directory)
    if config["assessment-mode"] == "total" or config["assessment-mode"] == "verify":
        print("Using total or verify entailment mode")
        model_simple = get_model(config["model"], config["temperature"], log_directory/'entailment_simple')
        model_complex = get_model(config["model"], config["temperature"], log_directory/'entailment_complex')
        model_default = get_model(config["model"], config["temperature"], log_directory/'entailment_default')
        model_simple_verify = get_model(config["model"], config["temperature"], log_directory/'entailment_simple_verify')
        model_complex_verify = get_model(config["model"], config["temperature"], log_directory/'entailment_complex_verify')
        model_default_verify = get_model(config["model"], config["temperature"], log_directory/'entailment_default_verify')
        model_default_no_fsl = get_model(config["model"], config["temperature"], log_directory/'entailment_default_no_fsl')
    
    
    # Perform naive entailment checking, generating counterexamples if necessary
    if config['entailment-mode'] == 'naive' and config['assessment-mode'] == 'postcondition-entailment':
        if not cex_path:
            if config["annotated"]:
                if config["annotated-type"] == "simple":
                    print("Using simple annotated entailment")
                    correctness = annotated_simple(description,  remove_functionality(annotated_func), model)
                elif config["annotated-type"] == "complex":
                    print("Using complex annotated entailment")
                    correctness = entailment_annotated.naive(model, description, return_str, annotated_func, module_name, config)
                else:
                    print(f"Annotated type {config['annotated-type']} not supported, only simple and complex are currently implemented")
                    raise NotImplementedError
            else:
                if config["fsl"]:
                    correctness = entailment.naive(model, description, postcondition, program, module_name, config)
                elif not config["fsl"]:
                    correctness = entailment_no_fsl.naive(model, description, postcondition, program, module_name, config)
                else:
                    print("Error: FSL should not have reached this function")
                    exit(1)
        else:
            if config["annotated"]:
                if config["annotated-type"] == "simple":
                    correctness = annotated_simple(description,  remove_functionality(annotated_func), model)
                elif config["annotated-type"] == "complex":
                    correctness = entailment_annotated.naive(model, description, return_str, annotated_func, module_name, config, cex_path)
                else :
                    print(f"Annotated type {config['annotated-type']} not supported, only simple and complex are currently implemented")
                    raise NotImplementedError
            else:
                if config["fsl"]:
                    correctness = entailment.naive(model, description, postcondition, program, module_name, config, cex_path)
                elif not config["fsl"]:
                    correctness = entailment_no_fsl.naive(model, description, postcondition, program, module_name, config, cex_path)
                else:
                    print("Error: FSL should not have reached this function")
                    exit(1)
            if not correctness[0] :
                reason = correctness[1].replace("Correctness: **False**", "")
                cex_generator.output_cex(model, description, postcondition, program, config, cex_path, module_name, reason)
        return correctness[0]
    elif config['entailment-mode'] == 'naive' and config['assessment-mode'] == 'total':
            #special case to save time when running the experiments
            correctness_simple = annotated_simple(description,  remove_functionality(annotated_func), model_simple)
            correctness_complex= entailment_annotated.naive(model_complex, description, return_str, annotated_func, module_name, config, cex_path)
            correctness_default = entailment.naive(model_default, description, postcondition, program, module_name, config, cex_path)
            correctness_default_no_fsl = entailment_no_fsl.naive(model_default_no_fsl, description, postcondition, program, module_name, config, cex_path)
            return [correctness_simple[0], correctness_complex[0], correctness_default[0], correctness_default_no_fsl[0]]
    elif config['entailment-mode'] == 'naive' and config['assessment-mode'] == 'verify':
            
            correctness_simple = annotated_simple(description,  remove_functionality(annotated_func), model_simple)
            correctness_complex= entailment_annotated.naive(model_complex, description, return_str, annotated_func, module_name, config, cex_path)
            correctness_default = entailment.naive(model_default, description, postcondition, program, module_name, config, cex_path)
            correctness_default_no_fsl = entailment_no_fsl.naive(model_default_no_fsl, description, postcondition, program, module_name, config, cex_path)

            correctness_naive, response_naive  = naive_question_with_response(description, program, model)
            correctness_naive_no_fsl, response_naive_no_fsl  = naive_question_no_fsl_with_response(description, program, model)
            correctness_simple_verify = verify_tree(model_simple_verify, description,  remove_functionality(annotated_func), program, response_naive, module_name, config, cex_path)
            correctness_complex_verify = verify_tree(model_complex_verify, description, annotated_func, program , response_naive , module_name, config, cex_path)
            correctness_default_verify = verify_function_summary(model_default_verify, description, postcondition, program, response_naive, module_name, config, cex_path)
            correctness_simple_no_fsl_verify = verify_tree(model_simple_verify, description,  remove_functionality(annotated_func), program, response_naive_no_fsl, module_name, config, cex_path)
            correctness_complex_no_fsl_verify= verify_tree(model_complex_verify, description, annotated_func, program , response_naive_no_fsl , module_name, config, cex_path)
            correctness_default_no_fsl_verify = verify_function_summary(model_default_verify, description, postcondition, program, response_naive_no_fsl, module_name, config, cex_path)
            #lets return a dicrionary with the results
            res_dict= {"naive": correctness_naive, "naive_no_fsl": correctness_naive_no_fsl , "simple": correctness_simple[0], "complex": correctness_complex[0], "default": correctness_default[0], "default_no_fsl": correctness_default_no_fsl[0], "simple_verify": correctness_simple_verify[0], "complex_verify": correctness_complex_verify[0], "default_verify": correctness_default_verify[0], "simple_no_fsl_verify": correctness_simple_no_fsl_verify[0], "complex_no_fsl_verify": correctness_complex_no_fsl_verify[0], "default_no_fsl_verify": correctness_default_no_fsl_verify[0]}
            print(res_dict)
            return res_dict
    print(f"Entailment mode {config['entailment-mode']} not supported, only naive is currently implemented")
    raise NotImplementedError

# Check if the postcondition implies compliance with the description using entailment
def check_entailment_mult_func(description, postconditions_list, functions_list, imports, global_code, module_name, config, log_directory, return_list, annotated_func_list,cex_path=None):
    model = get_model(config["model"], config["temperature"], log_directory)
    if config["assessment-mode"] == "total" or config["assessment-mode"] == "verify":
        model_simple = get_model(config["model"], config["temperature"], log_directory/'entailment_simple')
        model_complex = get_model(config["model"], config["temperature"], log_directory/'entailment_complex')
        model_default = get_model(config["model"], config["temperature"], log_directory/'entailment_default')
        model_simple_verify = get_model(config["model"], config["temperature"], log_directory/'entailment_simple_verify')
        model_complex_verify = get_model(config["model"], config["temperature"], log_directory/'entailment_complex_verify')
        model_default_verify = get_model(config["model"], config["temperature"], log_directory/'entailment_default_verify')
        model_default_no_fsl = get_model(config["model"], config["temperature"], log_directory/'entailment_default_no_fsl')

    program= imports+"\n"
    total_post=""
    functions =""
    fuctions_simple=""
    annotated_program=""
    annotated_program_simple=""
    # for func in functions_list:
    #     program += func
    #add the global code to the last function in function list
    # functions_list[-1] += "\n" +global_code
    for index, post in enumerate(postconditions_list):
        program += f"#Function {index+1}:\n" + functions_list[index]+"\n\n"
        total_post+= f"Output hints for function number {index+1} : {post}+\n"
        functions += f"Function number {index+1} :\n Code:\n '''\n{functions_list[index]}\n''' \n\n Output hints for function{index+1}:  {post}\n"
        output_hints = f"Output hints for function number {index+1} : {post}+\n"
        fuctions_simple += f"Function number {index+1} :\n Code:\n '''\n{functions_list[index]}\n''' \n"
        annotated_program += f"#Function {index+1}:\n" + annotated_func_list[index]+"\n\n"
        annotated_program_simple += f"#Function {index+1}:\n" + remove_functionality(annotated_func_list[index])+"\n"

    if global_code != "":
        annotated_program = global_code + "\n\n" + annotated_program
        annotated_program_simple = global_code + "\n\n" + annotated_program_simple
        functions =  global_code + "\n\n" + functions
        
    if imports != "":
        annotated_program = imports + "\n\n" + annotated_program
        annotated_program_simple = imports + "\n\n" + annotated_program_simple
        functions =  imports + "\n\n" + functions
    
    # Perform naive entailment checking, generating counterexamples if necessary
    if config['entailment-mode'] == 'naive' and config['assessment-mode'] == 'postcondition-entailment':
        if not cex_path:
            if config["annotated"]:
                if config["annotated-type"] == "simple":
                    correctness = annotated_simple(description,  annotated_program_simple, model)
                elif config["annotated-type"] == "complex":
                    correctness = entailement_mult_func_annotated.naive_mult_func(model, description, annotated_program, module_name, config)
                else:
                    print(f"Annotated type {config['annotated-type']} not supported, only simple and complex are currently implemented")
                    raise NotImplementedError
            else:
                if config["fsl"]:
                    correctness = entailment_mult_func.naive_mult_func(model, description, functions, module_name, config)
                elif not config["fsl"]:
                    correctness = entailment_mult_func_no_fsl.naive_mult_func(model, description, functions, module_name, config)
                else:
                    print("Error: FSL should not have reached this function")
                    exit(1)
        
        else:
            if config["annotated"]:
                if config["annotated-type"] == "simple":
                    correctness = annotated_simple(description,  annotated_program_simple, model)
                elif config["annotated-type"] == "complex":
                    correctness = entailement_mult_func_annotated.naive_mult_func(model, description, annotated_program, module_name, config, cex_path)
                else:
                    print(f"Annotated type {config['annotated-type']} not supported, only simple and complex are currently implemented")
                    raise NotImplementedError
            else:
                if config["fsl"]:
                    correctness = entailment_mult_func.naive_mult_func(model, description, functions, module_name, config, cex_path)
                elif not config["fsl"]:
                    correctness = entailment_mult_func_no_fsl.naive_mult_func(model, description, functions, module_name, config, cex_path)
                else:
                    print("Error: FSL should not have reached this function")
                    exit(1)
            if not correctness[0] :
                reason = correctness[1].replace("Correctness: **False**", "")
                cex_generator.output_cex(model, description, total_post, program, config, cex_path, module_name, reason)
        return correctness[0]
    elif config['entailment-mode'] == 'naive' and config['assessment-mode'] == 'total':
            #special case to save time when running the experiments
            correctness_simple = annotated_simple(description,  annotated_program_simple, model_simple)
            correctness_complex= entailement_mult_func_annotated.naive_mult_func(model_complex, description, annotated_program, module_name, config, cex_path)
            correctness_default =entailment_mult_func.naive_mult_func(model_default, description, functions, module_name, config, cex_path)
            correctness_default_no_fsl =entailment_mult_func_no_fsl.naive_mult_func(model_default_no_fsl, description, functions, module_name, config, cex_path)
            return [correctness_simple[0], correctness_complex[0], correctness_default[0], correctness_default_no_fsl[0]]
    elif config['entailment-mode'] == 'naive' and config['assessment-mode'] == 'verify':
            correctness_simple = annotated_simple(description,  annotated_program_simple, model_simple)
            correctness_complex= entailement_mult_func_annotated.naive_mult_func(model_complex, description, annotated_program, module_name, config, cex_path)
            correctness_default =entailment_mult_func.naive_mult_func(model_default, description, functions, module_name, config, cex_path)
            correctness_default_no_fsl =entailment_mult_func_no_fsl.naive_mult_func(model_default_no_fsl, description, functions, module_name, config, cex_path)

            correctness_naive, response_naive  = naive_question_with_response(description, program, model)
            correctness_naive_no_fsl, response_naive_no_fsl  = naive_question_no_fsl_with_response(description, program, model)

            correctness_simple_verify = verify_tree(model_simple_verify, description,  annotated_program_simple, program, response_naive, module_name, config, cex_path)
            correctness_complex_verify= verify_tree(model_complex_verify, description, annotated_program, program , response_naive , module_name, config, cex_path)
            correctness_default_verify = verify_function_summary(model_default_verify, description, output_hints, program, response_naive, module_name, config, cex_path)
            correctness_simple_no_fsl_verify = verify_tree(model_simple_verify, description,  annotated_program_simple, program, response_naive_no_fsl, module_name, config, cex_path)
            correctness_complex_no_fsl_verify= verify_tree(model_complex_verify, description, annotated_program, program , response_naive_no_fsl , module_name, config, cex_path)
            correctness_default_no_fsl_verify = verify_function_summary(model_default_verify, description, output_hints, program, response_naive_no_fsl, module_name, config, cex_path)
            #lets return a dicrionary with the results
            res_dict= {"naive": correctness_naive, "naive_no_fsl": correctness_naive_no_fsl , "simple": correctness_simple[0], "complex": correctness_complex[0], "default": correctness_default[0], "default_no_fsl": correctness_default_no_fsl[0], "simple_verify": correctness_simple_verify[0], "complex_verify": correctness_complex_verify[0], "default_verify": correctness_default_verify[0], "simple_no_fsl_verify": correctness_simple_no_fsl_verify[0], "complex_no_fsl_verify": correctness_complex_no_fsl_verify[0], "default_no_fsl_verify": correctness_default_no_fsl_verify[0]}
            print(res_dict)
            return res_dict

    print(f"Entailment mode {config['entailment-mode']} not supported, only naive is currently implemented")
    raise NotImplementedError

# This is just the entry point to the program
if __name__ == "__main__":
    main()


