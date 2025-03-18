import argparse
import shutil
import json
import os
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
import node_base_style.complete
from  node_base_style.naive import naive_question, naive_question_with_response
from node_base_style.naive_no_fsl import naive_question_no_fsl, naive_question_no_fsl_confidence, naive_question_no_fsl_confidence_2, naive_question_no_fsl_with_response, naive_question_no_fsl_confidence_qwen, naive_question_no_fsl_no_cot, tester_call
from node_base_style.annotated_simple import annotated_simple
from node_base_style.single_post import single_post
from node_base_style.single_post_no_fsl import single_post_no_fsl
from verify_entailement import verify_tree ,verify_function_summary
from node_base_style.naive_test import naive_test, naive_test_verify_ans, test_agentcoder

import cex_generator
from textwrap import dedent
import ast
import os
import subprocess

import re
from testing_equivalence import assess_postcondition_equivalence

CAPTURES="""
import io
import sys

def capture_output(func, input_data):
    sys.stdin = io.StringIO(input_data)
    captured_output = io.StringIO()
    sys.stdout = captured_output
    func()
    sys.stdout = sys.__stdout__
    return captured_output.getvalue().strip()"""

CAPTURES1="""
import io
import sys
"""

CAPTURES2="""
def capture_output(func, input_data):
    sys.stdin = io.StringIO(input_data)
    captured_output = io.StringIO()
    sys.stdout = captured_output
    func()
    sys.stdout = sys.__stdout__
    return captured_output.getvalue().strip()"""

def load_test_cases(file_path):
    """Load test cases from a JSON file."""
    with open(file_path, "r") as f:
        return json.load(f)







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
        global_code = "GLOBAL"

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
        
    if "concat_simple" not in config:
        config["concat_simple"] = True
    else:
        if type(config["concat_simple"]) != bool:
            print("Error: concat_simple should be a boolean")
            return 
    if "COT" not in config:
        config["COT"] = True
    else:
        if type(config["COT"]) != bool:
            print("Error: COT should be a boolean")
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
        model = get_model("qwq-32b-preview", config["temperature"], log_directory)
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

# Assess if a program is consistent with the description using pre/postconditions and entailment checking
def assess(description, program, module_name, config, log_directory, cex_path):
    
    cleaned_program, imports = remove_imports_and_comments(program)
    tester_code =imports +"\n\n" + cleaned_program
    functions_dict = extract_functions(cleaned_program)
    # print("this is the functions dict", functions_dict)
    is_global=  False
    functions_list= functions_dict["functions"]
    global_code = functions_dict["global_code"]
    if global_code == "GLOBAL" : 
        global_code =""
        is_global= True
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

    if is_global:
        test_code =  CAPTURES1 +"\n"+ CAPTURES2+"\n\n"+ remade_program
        test_code_call =remade_program
    else:
        test_code = imports +"\n" + CAPTURES1 +"\n"+ CAPTURES2+"\n\n"+ cleaned_program
        test_code_call =imports +"\n" + cleaned_program

    if config['assessment-mode'] == 'naive-test':
        print("Using naive_test assessment mode")
        return compute_postcondition_naivetest(description, tester_code, program, config, log_directory)
    
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
    assert config['assessment-mode'] in {'postcondition-entailment', 'total', 'verify','naive-test'}

    
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
        print(f"Using {config['assessment-mode']} entailment mode")
        entailment_log_dir_simple = entailment_log_dir/'entailment_simple'
        entailment_log_dir_simple.mkdir(parents=True, exist_ok=True)
        entailment_log_dir_complex = entailment_log_dir/'entailment_complex'
        entailment_log_dir_complex.mkdir(parents=True, exist_ok=True)
        entailment_log_dir_default = entailment_log_dir/'entailment_summary'
        entailment_log_dir_default.mkdir(parents=True, exist_ok=True)
        entailment_log_dir_simple_verify = entailment_log_dir/'entailment_simple_verify'
        entailment_log_dir_simple_verify.mkdir(parents=True, exist_ok=True)
        entailment_log_dir_complex_verify = entailment_log_dir/'entailment_complex_verify'
        entailment_log_dir_complex_verify.mkdir(parents=True, exist_ok=True)
        entailment_log_dir_default_verify = entailment_log_dir/'entailment_summary_verify'
        entailment_log_dir_default_verify.mkdir(parents=True, exist_ok=True)
        entailment_log_dir_default_no_fsl = entailment_log_dir/'entailment_summary'
        entailment_log_dir_default_no_fsl.mkdir(parents=True, exist_ok=True)
        entailment_log_dir_naive_fsl= entailment_log_dir/'entailment_naive_fsl'
        entailment_log_dir_naive_fsl.mkdir(parents=True, exist_ok=True)
        entailment_log_dir_vanilla= entailment_log_dir/'entailment_vanilla'
        entailment_log_dir_vanilla.mkdir(parents=True, exist_ok=True)
        entailment_log_dir_vanilla= entailment_log_dir/'entailment_vanilla_no_cot'
        entailment_log_dir_vanilla.mkdir(parents=True, exist_ok=True)

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
    
def compute_postcondition_naivetest(description, program, original_program, config, log_directory):
    model = get_model(config["model"], config["temperature"], log_directory)
    if config['entailment-mode'] == "verify-answer":
        response = test_agentcoder(description, program, original_program, model)
        # response = naive_test_verify_ans(description, program, original_program, model)
    else:
        response = naive_test(description, program, model)
    return response

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
        if config["COT"]:
            response = naive_question_no_fsl(description, all_funcs, model)
        else:
            response = naive_question_no_fsl_no_cot(description, all_funcs, model)
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
            print("FSL is set to False")
            if config["COT"]:
                print("COT is set to TRUE")
                response = naive_question_no_fsl(description, program, model)
            else:
                print("COT is set to FALSE")
                response = naive_question_no_fsl_no_cot(description, program, model)
            #dont use few shot learning
            
    else:
        response = naive_question(description, program, model)
    
    return response

# Compute the postcondition from a precondition and program
def compute_postcondition(precondition, program, config, log_directory):
    model = get_model(config["model"], config["temperature"], log_directory)

    # Check the mode for postcondition generation and use the appropriate algorithm
    if config['postcondition-mode'] == 'hoarecot':
        sp_algorithms = {
            "comment-style": comment_style.compute_postcondition,
            "node-based-style": node_base_style.complete.compute_postcondition
        }
        # Select and execute the correct strategy
        sp = sp_algorithms[config['postcondition-cot-prompt']]
        
        return sp(model, precondition, program, config)
    else:
        raise NotImplementedError

# Check if the postcondition implies compliance with the description using entailment
def check_entailment(description, postcondition, program, module_name, config, log_directory, return_str, annotated_func, cex_path=None):
    model = get_model(config["model"], config["temperature"], log_directory)
    if config["assessment-mode"] == "total" or config["assessment-mode"] == "verify":
        print(f"Using {config['assessment-mode']} entailment mode")
        model_naive= get_model(config["model"], config["temperature"], log_directory/'entailment_naive_fsl')
        model_vanilla= get_model(config["model"], config["temperature"], log_directory/'entailment_vanilla')
        model_vanilla_no_cot= get_model(config["model"], config["temperature"], log_directory/'entailment_vanilla_no_cot')
        model_simple = get_model(config["model"], config["temperature"], log_directory/'entailment_simple')
        model_complex = get_model(config["model"], config["temperature"], log_directory/'entailment_complex')
        model_default = get_model(config["model"], config["temperature"], log_directory/'entailment_summary')
        model_simple_verify = get_model(config["model"], config["temperature"], log_directory/'entailment_simple_verify')
        model_complex_verify = get_model(config["model"], config["temperature"], log_directory/'entailment_complex_verify')
        model_default_verify = get_model(config["model"], config["temperature"], log_directory/'entailment_summary_verify')
        model_default_no_fsl = get_model(config["model"], config["temperature"], log_directory/'entailment_summary')
    
    
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
            correctness_naive_no_fsl_no_cot = naive_question_no_fsl_no_cot(description, program, model_vanilla_no_cot)

            correctness_naive, response_naive  = naive_question_with_response(description, program, model_naive)
            correctness_naive_no_fsl, response_naive_no_fsl  = naive_question_no_fsl_with_response(description, program, model_vanilla)
            correctness_simple_verify = verify_tree(model_simple_verify, description,  remove_functionality(annotated_func), program, response_naive, module_name, config, cex_path)
            correctness_complex_verify = verify_tree(model_complex_verify, description, annotated_func, program , response_naive , module_name, config, cex_path)
            correctness_default_verify = verify_function_summary(model_default_verify, description, postcondition, program, response_naive, module_name, config, cex_path)
            correctness_simple_no_fsl_verify = verify_tree(model_simple_verify, description,  remove_functionality(annotated_func), program, response_naive_no_fsl, module_name, config, cex_path)
            correctness_complex_no_fsl_verify= verify_tree(model_complex_verify, description, annotated_func, program , response_naive_no_fsl , module_name, config, cex_path)
            correctness_default_no_fsl_verify = verify_function_summary(model_default_verify, description, postcondition, program, response_naive_no_fsl, module_name, config, cex_path)
            #lets return a dicrionary with the results
            res_dict= {"naive": correctness_naive, "naive_no_fsl": correctness_naive_no_fsl , "vanilla_no_cot": correctness_naive_no_fsl_no_cot, "simple": correctness_simple[0], "complex": correctness_complex[0], "default": correctness_default[0], "default_no_fsl": correctness_default_no_fsl[0], "simple_verify": correctness_simple_verify[0], "complex_verify": correctness_complex_verify[0], "default_verify": correctness_default_verify[0], "simple_no_fsl_verify": correctness_simple_no_fsl_verify[0], "complex_no_fsl_verify": correctness_complex_no_fsl_verify[0], "default_no_fsl_verify": correctness_default_no_fsl_verify[0]}
            print(res_dict)
            return res_dict
    print(f"Entailment mode {config['entailment-mode']} not supported, only naive is currently implemented")
    raise NotImplementedError

# Check if the postcondition implies compliance with the description using entailment
def check_entailment_mult_func(description, postconditions_list, functions_list, imports, global_code, module_name, config, log_directory, return_list, annotated_func_list,cex_path=None):
    model = get_model(config["model"], config["temperature"], log_directory)
    if config["assessment-mode"] == "total" or config["assessment-mode"] == "verify":
        model_naive= get_model(config["model"], config["temperature"], log_directory/'entailment_naive_fsl')
        model_vanilla= get_model(config["model"], config["temperature"], log_directory/'entailment_vanilla')
        model_vanilla_no_cot = get_model(config["model"], config["temperature"], log_directory/'entailment_vanilla_no_cot')
        model_simple = get_model(config["model"], config["temperature"], log_directory/'entailment_simple')
        model_complex = get_model(config["model"], config["temperature"], log_directory/'entailment_complex')
        model_default = get_model(config["model"], config["temperature"], log_directory/'entailment_summary')
        model_simple_verify = get_model(config["model"], config["temperature"], log_directory/'entailment_simple_verify')
        model_complex_verify = get_model(config["model"], config["temperature"], log_directory/'entailment_complex_verify')
        model_default_verify = get_model(config["model"], config["temperature"], log_directory/'entailment_summary_verify')
        model_default_no_fsl = get_model(config["model"], config["temperature"], log_directory/'entailment_summary')

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
            correctness_naive_no_fsl_no_cot = naive_question_no_fsl_no_cot(description, program, model_vanilla_no_cot)
            correctness_naive, response_naive  = naive_question_with_response(description, program, model_naive)
            correctness_naive_no_fsl, response_naive_no_fsl  = naive_question_no_fsl_with_response(description, program, model_vanilla)

            correctness_simple_verify = verify_tree(model_simple_verify, description,  annotated_program_simple, program, response_naive, module_name, config, cex_path)
            correctness_complex_verify= verify_tree(model_complex_verify, description, annotated_program, program , response_naive , module_name, config, cex_path)
            correctness_default_verify = verify_function_summary(model_default_verify, description, output_hints, program, response_naive, module_name, config, cex_path)
            correctness_simple_no_fsl_verify = verify_tree(model_simple_verify, description,  annotated_program_simple, program, response_naive_no_fsl, module_name, config, cex_path)
            correctness_complex_no_fsl_verify= verify_tree(model_complex_verify, description, annotated_program, program , response_naive_no_fsl , module_name, config, cex_path)
            correctness_default_no_fsl_verify = verify_function_summary(model_default_verify, description, output_hints, program, response_naive_no_fsl, module_name, config, cex_path)
            #lets return a dicrionary with the results
            res_dict= {"naive": correctness_naive, "naive_no_fsl": correctness_naive_no_fsl , "vanilla_no_cot": correctness_naive_no_fsl_no_cot, "simple": correctness_simple[0], "complex": correctness_complex[0], "default": correctness_default[0], "default_no_fsl": correctness_default_no_fsl[0], "simple_verify": correctness_simple_verify[0], "complex_verify": correctness_complex_verify[0], "default_verify": correctness_default_verify[0], "simple_no_fsl_verify": correctness_simple_no_fsl_verify[0], "complex_no_fsl_verify": correctness_complex_no_fsl_verify[0], "default_no_fsl_verify": correctness_default_no_fsl_verify[0]}
            print(res_dict)
            return res_dict

    print(f"Entailment mode {config['entailment-mode']} not supported, only naive is currently implemented")
    raise NotImplementedError

# This is just the entry point to the program
if __name__ == "__main__":
    main()


