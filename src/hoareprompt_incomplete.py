import ast
import sys


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
        return "function_start"

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
                placeholder = "if condition:\n    pass\n"
            elif first_part_lines[0].strip().startswith("elif"):
                placeholder = "if condition:\n    pass\n"
            elif first_part_lines[0].strip().startswith("except"):
                placeholder = "try:\n    pass\n"
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
            return lines + [" " * (indent + 4) + "pass"]
            
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
                lines.append( " " * (line_indent) + "pass")
            elif last_line.startswith("elif "):
                # Add pass and else block
                lines.concat([
                    " " * (line_indent + 4) + "pass",
                    " " * line_indent + "else:",
                    " " * (line_indent + 4) + "pass",
                ])
                
            elif last_line.startswith("else:"):
                # Add pass for else block
                lines.append( " " * (line_indent + 4) + "pass")
            elif last_line.startswith("except"):
                # Add pass for except block
                lines.append(" " * (line_indent + 4) + "pass")
            else:
                # General case: add a pass statement for any other block
                lines.append(" " * (line_indent + 4) + "pass")
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
                lines.append(" " * try_indent + "except Exception as e:")
                lines.append(" " * (try_indent + 4) + "pass")

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
                lines.append( " " * elif_indent + "else:")
                lines.append( " " * (elif_indent + 4) + "pass")


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
        if detect_global_or_function_start(first_part_lines) == "global_start":
            print("Global code detected.")
            print(f"First part lines: {first_part_lines}")
            return process_first_part(first_part_lines, remaining_lines)
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
            ast.parse(snippet)
            print("The snippet was made parsable.")
        except SyntaxError as e:
            print("The snippet was not made parsable.")
        
        print(snippet)
test()