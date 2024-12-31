import ast

from textwrap import dedent
def remove_imports_and_comments(script: str) -> tuple:
    """
    Remove import statements and general comments, but retain '# ADDED LINE' comments
    at the end of lines. Renames function names for consistency.
    """
    # Parse the script into an AST
    tree = ast.parse(script)
    lines = script.splitlines()
    added_lines =[]
    # Initialize storage for import statements and function name mapping
    imports = []
    function_names = []
    function_mapping = {}

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
            print(f"Start index found: {start_index}")
        else:
            print(f"Start index: {start_index}")
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
    print(f"Added start line: {added_start_line}")
    print(f"Added end line: {added_end_line}")
    print(f"annotated lines 0: {annotated_lines[0]}")
   
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


code="""
def find_max(numbers):
    max_value = 0
    for num in numbers:
        if num > max_value:
            max_value = num # ADDED LINE
    return max_value

"""
# cleaned, imp = remove_imports_and_comments(code)
# print(cleaned)
# ret =extract_functions(cleaned)
# print(ret["functions"])

code1 = """
def func(): # ADDED LINE
    for num in numbers:
        if num > max_value:
            max_value = num
        return max_value
"""

code2 = """
def func():
    for num in numbers:
        if num > max_value:
            max_value = num
        
        return max_value
        
    #State of the program after the  for loop has been executed: `max_value` is the maximum value present in the list `numbers`, `numbers` is an empty list if the loop did not execute, otherwise it is a list that no longer contains any elements greater than `max_value`.
#Overall this is what the function does:The function `func()` accepts a non-empty list of integers `numbers` and an initialized variable `max_value`. It iterates through each element in `numbers` and updates `max_value` to be the highest value found in `numbers`. After the loop, it returns `max_value` as the maximum value present in the original `numbers` list. However, the function does not correctly modify `numbers` to remove all elements greater than `max_value`; instead, it prematurely returns `max_value` during the first iteration of the loop. As a result, `numbers` remains unchanged. The function also fails to handle the case where `numbers` might be empty initially, although this case is not explicitly stated in the given annotations.
"""

print(remove_added_lines(code1, code2))