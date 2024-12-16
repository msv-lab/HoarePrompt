import os
import pandas as pd
import ast
import re
from textwrap import dedent
import json
from pathlib import Path
from model import get_model

from verify_entailement import verify_tree ,verify_function_summary


def clean_string(input_string):
    # Find all instances of lines starting with '#Overall this is what the function does:'
    removed_strings = re.findall(r"#Overall this is what the function does:(.*)", input_string)
    
    # Remove these lines from the original string
    cleaned_string = re.sub(r"#Overall this is what the function does:.*\n", "", input_string)
    # print(removed_strings)
    # print(cleaned_string)
    return cleaned_string, removed_strings
def remove_imports_and_comments(script: str) -> tuple:
    # Parse the script into an AST
    tree = ast.parse(script)

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

    # Generate cleaned script without comments and renamed functions
    script_no_comments = "\n".join(
        line for line in script.splitlines() if not line.strip().startswith("#")
    )
    cleaned_script = ast.unparse(tree)

    # Join imports as a separate string
    imports_str = "\n".join(imports)

    return cleaned_script.strip(), imports_str.strip()

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

def process_directory(input_dir):
    # Verify that the input directory exists
    if not os.path.isdir(input_dir):
        raise FileNotFoundError(f"The directory '{input_dir}' does not exist.")

    # Read the CSV file in the input directory
    csv_files = [f for f in os.listdir(input_dir) if f.endswith('.csv')]
    if not csv_files:
        raise FileNotFoundError("No CSV file found in the input directory.")
    csv_file = os.path.join(input_dir, csv_files[0])

    json_files = [f for f in os.listdir(input_dir) if f.endswith('.json')]
    if not json_files:
        raise FileNotFoundError("No json file found in the input directory.")
    
    json_file = os.path.join(input_dir, json_files[0])
    #load the json file
    with open(json_file) as f:
        config = json.load(f)

    total_dataframe = pd.read_csv(csv_file)
    #in the dataframe add 6 more columns "simple verify", "complex verify", "default verify", "simple verify no fsl", "complex verify no fsl", "default verify no fsl"
    total_dataframe["simple_verify"] = None
    total_dataframe["complex_verify"] = None
    total_dataframe["default_verify"] = None
    total_dataframe["simple_verify_no_fsl"] = None
    total_dataframe["complex_verify_no_fsl"] = None
    total_dataframe["default_verify_no_fsl"] = None
    print(f"CSV file '{csv_file}' loaded successfully into 'total_dataframe'.")

    

    # Iterate over first-level subdirectories
    for subdir in [d for d in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir, d))]:
        subdir_path = os.path.join(input_dir, subdir)

        # Check for the '{subdir}_naive' directory
        naive_dir = os.path.join(subdir_path, f"{subdir}_naive")
        if not os.path.isdir(naive_dir):
            print(f"Skipping '{subdir_path}', no directory named '{subdir}_naive'.")
            continue

        # Check for the 'gpt-4o' and 'llama3-70b' directories
        gpt_dir = os.path.join(naive_dir, "gpt-4o")
        llama_dir = os.path.join(naive_dir, "llama3-70b")

        if not os.path.isdir(gpt_dir) or not os.path.isdir(llama_dir):
            print(f"Skipping '{naive_dir}', required subdirectories ('gpt-4o', 'llama3-70b') not found.")
            continue

        # Read the '0000.response' files
        naive_gpt_file = os.path.join(gpt_dir, "0000.response.md")
        naive_llama_file = os.path.join(llama_dir, "0000.response.md")

        naive_gpt = None
        naive_llama = None

        if os.path.isfile(naive_gpt_file):
            with open(naive_gpt_file, 'r') as file:
                naive_gpt = file.read().strip()
        else:
            print(f"File '{naive_gpt_file}' not found.")

        if os.path.isfile(naive_llama_file):
            with open(naive_llama_file, 'r') as file:
                naive_llama = file.read().strip()
        else:
            print(f"File '{naive_llama_file}' not found.")

        # Output results
        print(f"Subdirectory '{subdir}':")
        print(f"  naive_gpt: {naive_gpt}")
        print(f"  naive_llama: {naive_llama}")


        #do the same for naive_no_fsl
        naive_nfsl_dir = os.path.join(subdir_path, f"{subdir}_naive_no_fsl")
        if not os.path.isdir(naive_nfsl_dir):
            print(f"Skipping '{subdir_path}', no directory named '{subdir}_naive_no_fsl'.")
            continue

        # Check for the 'gpt-4o' and 'llama3-70b' directories
        gpt_dir = os.path.join(naive_nfsl_dir, "gpt-4o")
        llama_dir = os.path.join(naive_nfsl_dir, "llama3-70b")

        if not os.path.isdir(gpt_dir) or not os.path.isdir(llama_dir):
            print(f"Skipping '{naive_nfsl_dir}', required subdirectories ('gpt-4o', 'llama3-70b') not found.")
            continue

        # Read the '0000.response' files
        naive_no_fsl_gpt_file = os.path.join(gpt_dir, "0000.response.md")
        naive_no_fsl_llama_file = os.path.join(llama_dir, "0000.response.md")

        naive_no_fsl_gpt = None
        naive_no_fsl_llama = None

        if os.path.isfile(naive_no_fsl_gpt_file):
            with open(naive_no_fsl_gpt_file, 'r') as file:
                naive_no_fsl_gpt = file.read().strip()
        else:
            print(f"File '{naive_no_fsl_gpt_file}' not found.")

        if os.path.isfile(naive_no_fsl_llama_file):
            with open(naive_no_fsl_llama_file, 'r') as file:
                naive_no_fsl_llama = file.read().strip()
        else:
            print(f"File '{naive_no_fsl_llama_file}' not found.")

        # Output results
        print(f"Subdirectory '{subdir}':")
        print(f"  naive no fsl_gpt: {naive_no_fsl_gpt}")
        print(f"  naive_no_fsl_llama: {naive_no_fsl_llama}")


        noraml_dir = os.path.join(subdir_path, f"{subdir}_normal")
        if not os.path.isdir(noraml_dir):
            print(f"Skipping '{subdir_path}', no directory named '{subdir}_normal'.")
            continue

        # Check for the 'gpt-4o' and 'llama3-70b' directories
        gpt_dir = os.path.join(noraml_dir, "gpt-4o")
        llama_dir = os.path.join(noraml_dir, "llama3-70b")

        if not os.path.isdir(gpt_dir) or not os.path.isdir(llama_dir):
            print(f"Skipping '{noraml_dir}', required subdirectories ('gpt-4o', 'llama3-70b') not found.")
            continue

        # Read the 'description' files
        normal_gpt_description_file = os.path.join(gpt_dir, "description.txt")
        normal_llama_description_file = os.path.join(llama_dir, "description.txt")

        normal_gpt_description = None
        normal_llama_description = None

        if os.path.isfile(normal_gpt_description_file):
            with open(normal_gpt_description_file, 'r') as file:
                normal_gpt_description = file.read().strip()
        else:
            print(f"File '{normal_gpt_description_file}' not found.")

        if os.path.isfile(normal_llama_description_file):
            with open(normal_llama_description_file, 'r') as file:
                normal_llama_description = file.read().strip()
        else:
            print(f"File '{normal_llama_description_file}' not found.")

        # Output results
        print(f"Subdirectory '{subdir}':")
        print(f"  gpt description: {normal_gpt_description}")
        print(f"  llama description: {normal_llama_description}")

        # Read the 'program' files
        normal_gpt_program_file = os.path.join(gpt_dir, f"{subdir}.py")
        normal_llama_program_file = os.path.join(llama_dir, f"{subdir}.py")

        normal_gpt_program = None
        normal_llama_program = None

        if os.path.isfile(normal_gpt_program_file):
            with open(normal_gpt_program_file, 'r') as file:
                normal_gpt_program = file.read().strip()
        else:
            print(f"File '{normal_gpt_program_file}' not found.")

        if os.path.isfile(normal_llama_program_file):
            with open(normal_llama_program_file, 'r') as file:
                normal_llama_program = file.read().strip()
        else:
            print(f"File '{normal_llama_program_file}' not found.")

        # Output results
        print(f"Subdirectory '{subdir}':")
        print(f"  gpt program: {normal_gpt_program}")
        print(f"  llama program: {normal_llama_program}")

        # Read the 'program' files
        normal_gpt_program_cleaned_file = os.path.join(gpt_dir, f"{subdir}_cleaned.py")
        normal_llama_program_cleaned_file = os.path.join(llama_dir, f"{subdir}_cleaned.py")

        normal_gpt_program_cleaned = None
        normal_llama_program_cleaned = None

        if os.path.isfile(normal_gpt_program_cleaned_file):
            with open(normal_gpt_program_cleaned_file, 'r') as file:
                normal_gpt_program_cleaned = file.read().strip()
        else:
            print(f"File '{normal_gpt_program_cleaned_file}' not found.")

        if os.path.isfile(normal_llama_program_cleaned_file):
            with open(normal_llama_program_cleaned_file, 'r') as file:
                normal_llama_program_cleaned = file.read().strip()
        else:
            print(f"File '{normal_llama_program_cleaned_file}' not found.")

        # Output results
        print(f"Subdirectory '{subdir}':")
        print(f"  gpt program_cleaned: {normal_gpt_program_cleaned}")
        print(f"  llama program_cleaned: {normal_llama_program_cleaned}")

        # Read the 'annoated' files
        normal_gpt_annotated_file = os.path.join(gpt_dir, f"annotated_func.py")
        normal_llama_annotated_file = os.path.join(llama_dir, f"annotated_func.py")

        normal_gpt_annotated = None
        normal_llama_annotated = None

        if os.path.isfile(normal_gpt_annotated_file):
            with open(normal_gpt_annotated_file, 'r') as file:
                normal_gpt_annotated = file.read().strip()
        else:
            print(f"File '{normal_gpt_annotated_file}' not found.")

        if os.path.isfile(normal_llama_annotated_file):
            with open(normal_llama_annotated_file, 'r') as file:
                normal_llama_annotated = file.read().strip()
        else:
            print(f"File '{normal_llama_annotated_file}' not found.")

        # Output results
        print(f"Subdirectory '{subdir}':")
        print(f"  gpt annotated: {normal_gpt_annotated}")
        print(f"  llama annotated: {normal_llama_annotated}")



        cleaned_program_gpt, imports_gpt = remove_imports_and_comments(normal_gpt_program)
    
        functions_dict_gpt = extract_functions(cleaned_program_gpt)
        functions_list_gpt= functions_dict_gpt["functions"]
        global_code_gpt = functions_dict_gpt["global_code"]

        cleaned_program_llama, imports_llama = remove_imports_and_comments(normal_llama_program)
    
        functions_dict_llama = extract_functions(cleaned_program_llama)
        functions_list_llama= functions_dict_llama["functions"]
        global_code_llama = functions_dict_llama["global_code"]
        print(total_dataframe[total_dataframe['Task ID'].isin(['62', 62, 'Mbpp_62'])])
        # print(total_dataframe['Task ID'].dtype)
        # print(type(subdir))

        gpt_dir = os.path.join(noraml_dir, "gpt-4o")
        llama_dir = os.path.join(noraml_dir, "llama3-70b")
        gpt_dir_temp= os.path.join(gpt_dir, "check_entailment")
       # i want to make entailment_gpt_log_dir_simple_verify into a path to do mkdir

        entailment_gpt_log_dir_simple_verify =  Path(gpt_dir_temp)/'entailment_simple_verify'
        entailment_gpt_log_dir_simple_verify.mkdir(parents=True, exist_ok=True)
        print("done1")
        entailment_gpt_log_dir_complex_verify = Path(gpt_dir_temp)/'entailment_complex_verify'
        entailment_gpt_log_dir_complex_verify.mkdir(parents=True, exist_ok=True)
        entailment_gpt_log_dir_default_verify = Path(gpt_dir_temp)/'entailment_default_verify'
        entailment_gpt_log_dir_default_verify.mkdir(parents=True, exist_ok=True)
        

        llama_temp_dir = os.path.join(llama_dir, "check_entailment")
        
        entailment_llama_log_dir_simple_verify = Path(llama_temp_dir)/'entailment_simple_verify'
        entailment_llama_log_dir_simple_verify.mkdir(parents=True, exist_ok=True)
        entailment_llama_log_dir_complex_verify = Path(llama_temp_dir)/'entailment_complex_verify'
        entailment_llama_log_dir_complex_verify.mkdir(parents=True, exist_ok=True)
        entailment_llama_log_dir_default_verify = Path(llama_temp_dir)/'entailment_default_verify'
        entailment_llama_log_dir_default_verify.mkdir(parents=True, exist_ok=True)
        
        print("done2")
        remade_program_gpt=""
        if imports_gpt != "":
            remade_program_gpt += imports_gpt + "\n\n"
            normal_gpt_annotated = imports_gpt + "\n\n" + normal_gpt_annotated
        if global_code_gpt != "":
            remade_program_gpt += global_code_gpt + "\n\n"
            normal_gpt_annotated = global_code_gpt + "\n\n" + normal_gpt_annotated
        for func in functions_list_gpt:
            remade_program_gpt += func + "\n\n"
        
        remade_program_llama=""
        if imports_llama != "":
            remade_program_llama += imports_llama + "\n\n"
            normal_llama_annotated = imports_llama + "\n\n" + normal_llama_annotated
        if global_code_llama != "":
            remade_program_llama += global_code_llama + "\n\n"
            normal_llama_annotated = global_code_llama + "\n\n" + normal_llama_annotated
        for func in functions_list_llama:
            remade_program_llama += func + "\n\n"

        annoatated_simple_gpt, functionalities_gpt =clean_string(normal_gpt_annotated)
        annoatated_simple_llama, functionalities_llama =clean_string(normal_llama_annotated)
        
        functionality_gpt =""
        for index, func in enumerate(functionalities_gpt):
            functionality_gpt += f"Output hint for function_{index}: {func} + \n\n"

        functionality_llama =""
        for index, func in enumerate(functionalities_llama):
            functionality_llama += f"Output hint for function_{index}: {func} + \n\n"

        model_simple_verify_gpt = get_model(config["model"], config["temperature"], entailment_gpt_log_dir_simple_verify)
        model_complex_verify_gpt = get_model(config["model"], config["temperature"],entailment_gpt_log_dir_complex_verify)
        model_default_verify_gpt = get_model(config["model"], config["temperature"], entailment_gpt_log_dir_default_verify)

        model_simple_verify_llama = get_model(config["model"], config["temperature"], entailment_llama_log_dir_simple_verify)
        model_complex_verify_llama = get_model(config["model"], config["temperature"],entailment_llama_log_dir_complex_verify)
        model_default_verify_llama = get_model(config["model"], config["temperature"], entailment_llama_log_dir_default_verify)

        correctness_simple_verify_gpt = verify_tree(model_simple_verify_gpt, normal_gpt_description, annoatated_simple_gpt , remade_program_gpt, naive_gpt, subdir, config, "")
        correctness_complex_verify_gpt = verify_tree(model_complex_verify_gpt, normal_gpt_description, normal_gpt_annotated, remade_program_gpt , naive_gpt , subdir, config, "")
        correctness_default_verify_gpt = verify_function_summary(model_default_verify_gpt, normal_gpt_description, "\n"+normal_gpt_description, remade_program_gpt, naive_gpt, subdir, config, "")
        correctness_simple_no_fsl_verify_gpt = verify_tree(model_simple_verify_gpt, normal_gpt_description, annoatated_simple_gpt , remade_program_gpt, naive_no_fsl_gpt, subdir, config, "")
        correctness_complex_no_fsl_verify_gpt = verify_tree(model_complex_verify_gpt, normal_gpt_description, normal_gpt_annotated, remade_program_gpt , naive_no_fsl_gpt , subdir, config, "")
        correctness_default_no_fsl_verify_gpt = verify_function_summary(model_default_verify_gpt, normal_gpt_description, "\n"+normal_gpt_description, remade_program_gpt, naive_no_fsl_gpt, subdir, config, "")

        correctness_simple_verify_llama = verify_tree(model_simple_verify_llama, normal_llama_description, annoatated_simple_llama , remade_program_llama, naive_llama, subdir, config, "")
        correctness_complex_verify_llama = verify_tree(model_complex_verify_llama, normal_llama_description, normal_llama_annotated, remade_program_llama , naive_llama , subdir, config, "")
        correctness_default_verify_llama = verify_function_summary(model_default_verify_llama, normal_llama_description, "\n"+normal_llama_description, remade_program_llama, naive_llama, subdir, config, "")
        correctness_simple_no_fsl_verify_llama = verify_tree(model_simple_verify_llama, normal_llama_description, annoatated_simple_llama , remade_program_llama, naive_no_fsl_llama, subdir, config, "")
        correctness_complex_no_fsl_verify_llama = verify_tree(model_complex_verify_llama, normal_llama_description, normal_llama_annotated, remade_program_llama , naive_no_fsl_llama , subdir, config, "")
        correctness_default_no_fsl_verify_llama = verify_function_summary(model_default_verify_llama, normal_llama_description, "\n"+normal_llama_description, remade_program_llama, naive_no_fsl_llama, subdir, config, "")
        print(f"the correctness_simple_verify_gpt is {correctness_simple_verify_gpt[0]}")

        # #find the row in the dataframe where Task ID == subdir and model_created == gpt-4o. if it does not exist find the row in the dataframe where Task ID == Mbpp_{subdir} and model_created == gpt-4o. 
        # #set the values of the columns "simple verify", "complex verify", "default verify", "simple verify no fsl", "complex verify no fsl", "default verify no fsl" to the corresponding correctness valu
        # total_dataframe.loc[(total_dataframe['Task ID'] == str(subdir)) & (total_dataframe['model_created'] == 'gpt-4o'), 'simple_verify'] = correctness_simple_verify_gpt[0]
        # total_dataframe.loc[(total_dataframe['Task ID'] == subdir) & (total_dataframe['model_created'] == 'gpt-4o'), 'complex_verify'] = correctness_complex_verify_gpt[0]
        # total_dataframe.loc[(total_dataframe['Task ID'] == subdir) & (total_dataframe['model_created'] == 'gpt-4o'), 'default_verify'] = correctness_default_verify_gpt[0]
        # total_dataframe.loc[(total_dataframe['Task ID'] == subdir) & (total_dataframe['model_created'] == 'gpt-4o'), 'simple_verify_no_fsl'] = correctness_simple_no_fsl_verify_gpt[0]
        # total_dataframe.loc[(total_dataframe['Task ID'] == subdir) & (total_dataframe['model_created'] == 'gpt-4o'), 'complex_verify_no_fsl'] = correctness_complex_no_fsl_verify_gpt[0]
        # total_dataframe.loc[(total_dataframe['Task ID'] == subdir) & (total_dataframe['model_created'] == 'gpt-4o'), 'default_verify_no_fsl'] = correctness_default_no_fsl_verify_gpt[0]
        # total_dataframe.loc[(total_dataframe['Task ID'] == f"Mbpp_{subdir}") & (total_dataframe['model_created'] == 'gpt-4o'), 'simple_verify'] = correctness_simple_verify_gpt[0]
        # total_dataframe.loc[(total_dataframe['Task ID'] == f"Mbpp_{subdir}") & (total_dataframe['model_created'] == 'gpt-4o'), 'complex_verify'] = correctness_complex_verify_gpt[0]
        # total_dataframe.loc[(total_dataframe['Task ID'] == f"Mbpp_{subdir}") & (total_dataframe['model_created'] == 'gpt-4o'), 'default_verify'] = correctness_default_verify_gpt[0]
        # total_dataframe.loc[(total_dataframe['Task ID'] == f"Mbpp_{subdir}") & (total_dataframe['model_created'] == 'gpt-4o'), 'simple_verify_no_fsl'] = correctness_simple_no_fsl_verify_gpt[0]
        # total_dataframe.loc[(total_dataframe['Task ID'] == f"Mbpp_{subdir}") & (total_dataframe['model_created'] == 'gpt-4o'), 'complex_verify_no_fsl'] = correctness_complex_no_fsl_verify_gpt[0]
        # total_dataframe.loc[(total_dataframe['Task ID'] == f"Mbpp_{subdir}") & (total_dataframe['model_created'] == 'gpt-4o'), 'default_verify_no_fsl'] = correctness_default_no_fsl_verify_gpt[0]




        # #find the row in the dataframe where Task ID == subdir and model_created ==  llama3-70bllama3-70b
        # total_dataframe.loc[(total_dataframe['Task ID'] == subdir) & (total_dataframe['model_created'] == 'llama3-70bllama3-70b'), 'simple_verify'] = correctness_simple_verify_llama[0]
        # total_dataframe.loc[(total_dataframe['Task ID'] == subdir) & (total_dataframe['model_created'] == 'llama3-70bllama3-70b'), 'complex_verify'] = correctness_complex_verify_llama[0]
        # total_dataframe.loc[(total_dataframe['Task ID'] == subdir) & (total_dataframe['model_created'] == 'llama3-70bllama3-70b'), 'default_verify'] = correctness_default_verify_llama[0]
        # total_dataframe.loc[(total_dataframe['Task ID'] == subdir) & (total_dataframe['model_created'] == 'llama3-70bllama3-70b'), 'simple_verify_no_fsl'] = correctness_simple_no_fsl_verify_llama[0]
        # total_dataframe.loc[(total_dataframe['Task ID'] == subdir) & (total_dataframe['model_created'] == 'llama3-70bllama3-70b'), 'complex_verify_no_fsl'] = correctness_complex_no_fsl_verify_llama[0]
        # total_dataframe.loc[(total_dataframe['Task ID'] == subdir) & (total_dataframe['model_created'] == 'llama3-70bllama3-70b'), 'default_verify_no_fsl'] = correctness_default_no_fsl_verify_llama[0]
        # total_dataframe.loc[(total_dataframe['Task ID'] == f"Mbpp_{subdir}") & (total_dataframe['model_created'] == 'llama3-70bllama3-70b'), 'simple_verify'] = correctness_simple_verify_llama[0]
        # total_dataframe.loc[(total_dataframe['Task ID'] == f"Mbpp_{subdir}") & (total_dataframe['model_created'] == 'llama3-70bllama3-70b'), 'complex_verify'] = correctness_complex_verify_llama[0]
        # total_dataframe.loc[(total_dataframe['Task ID'] == f"Mbpp_{subdir}") & (total_dataframe['model_created'] == 'llama3-70bllama3-70b'), 'default_verify'] = correctness_default_verify_llama[0]
        # total_dataframe.loc[(total_dataframe['Task ID'] == f"Mbpp_{subdir}") & (total_dataframe['model_created'] == 'llama3-70bllama3-70b'), 'simple_verify_no_fsl'] = correctness_simple_no_fsl_verify_llama[0]
        # total_dataframe.loc[(total_dataframe['Task ID'] == f"Mbpp_{subdir}") & (total_dataframe['model_created'] == 'llama3-70bllama3-70b'), 'complex_verify_no_fsl'] = correctness_complex_no_fsl_verify_llama[0]
        # total_dataframe.loc[(total_dataframe['Task ID'] == f"Mbpp_{subdir}") & (total_dataframe['model_created'] == 'llama3-70bllama3-70b'), 'default_verify_no_fsl'] = correctness_default_no_fsl_verify_llama[0]

        # Define the columns to update and their corresponding correctness values for GPT
        gpt_columns_to_update = {
            'simple_verify': correctness_simple_verify_gpt[0],
            'complex_verify': correctness_complex_verify_gpt[0],
            'default_verify': correctness_default_verify_gpt[0],
            'simple_verify_no_fsl': correctness_simple_no_fsl_verify_gpt[0],
            'complex_verify_no_fsl': correctness_complex_no_fsl_verify_gpt[0],
            'default_verify_no_fsl': correctness_default_no_fsl_verify_gpt[0]
        }

        # Define the columns to update and their corresponding correctness values for Llama
        llama_columns_to_update = {
            'simple_verify': correctness_simple_verify_llama[0],
            'complex_verify': correctness_complex_verify_llama[0],
            'default_verify': correctness_default_verify_llama[0],
            'simple_verify_no_fsl': correctness_simple_no_fsl_verify_llama[0],
            'complex_verify_no_fsl': correctness_complex_no_fsl_verify_llama[0],
            'default_verify_no_fsl': correctness_default_no_fsl_verify_llama[0]
        }
        try:
            subdir_num = int(subdir)  # Ensure subdir matches the type of Task ID
        except ValueError:
            raise ValueError(f"subdir '{subdir}' is not a valid integer.")


                # Helper function to update rows or log errors
        def update_or_log_error(model_name, subdir, columns_to_update, model_column_value):
            # Ensure subdir is treated as an integer for comparison
            subdir = int(subdir)  # Convert to integer to match Task ID type

            # Check for Task ID == subdir
            row_found_subdir = total_dataframe.loc[
                (total_dataframe['Task ID'] == subdir) & (total_dataframe['model_created'] == model_column_value)
            ]

            # Check for Task ID == f"Mbpp_{subdir}"
            row_found_mbpp = total_dataframe.loc[
                (total_dataframe['Task ID'] == f"Mbpp_{subdir}") & (total_dataframe['model_created'] == model_column_value)
            ]

            # Update the rows if found
            if not row_found_subdir.empty:
                for column, value in columns_to_update.items():
                    total_dataframe.loc[
                        (total_dataframe['Task ID'] == subdir) & (total_dataframe['model_created'] == model_column_value),
                        column
                    ] = value
            elif not row_found_mbpp.empty:
                for column, value in columns_to_update.items():
                    total_dataframe.loc[
                        (total_dataframe['Task ID'] == f"Mbpp_{subdir}") & (total_dataframe['model_created'] == model_column_value),
                        column
                    ] = value
            else:
                # If no matching rows are found, log an error
                with open("error.txt", "a") as error_file:
                    error_file.write(
                        f"Error: No matching row found for Task ID '{subdir}' or 'Mbpp_{subdir}' with model_created == '{model_column_value}'.\n"
                    )

                        

        # Update for gpt-4o
        update_or_log_error('gpt-4o', subdir_num, gpt_columns_to_update, 'gpt-4o')

        # Update for llama3-70bllama3-70b
        update_or_log_error('llama3-70bllama3-70b', subdir_num, llama_columns_to_update, 'llama3-70b')


    # Save the updated dataframe to a new CSV file
    output_csv = os.path.join(input_dir, "total_results.csv")
    total_dataframe.to_csv(output_csv, index=False)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <input_directory>")
        sys.exit(1)

    input_directory = sys.argv[1]

    try:
        process_directory(input_directory)
    except Exception as e:
        print(f"Error: {e}")
