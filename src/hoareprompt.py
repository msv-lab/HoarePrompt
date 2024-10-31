import argparse
import shutil
import json
import os
from pathlib import Path
from model import get_model

import precondition_extractor
import entailment
import entailment_mult_func
import comment_style
import node_base_style.complete
from  node_base_style.naive import naive_question
import cex_generator

import re


def remove_imports_and_comments(script: str) -> tuple:
    # Extract import statements
    imports = re.findall(r'^\s*(import .+|from .+ import .+)', script, flags=re.MULTILINE)
    imports_str = "\n".join(imports)
    
    # Remove import statements from the script
    script_no_imports = re.sub(r'^\s*import .*\n?|^\s*from .*\n?', '', script, flags=re.MULTILINE)
    
    # Remove single-line comments
    script_no_comments = re.sub(r'#.*', '', script_no_imports)
    
    # Remove multi-line comments (both """ ... """ and ''' ... ''')
    script_cleaned = re.sub(r'(""".*?"""|\'\'\'.*?\'\'\')', '', script_no_comments, flags=re.DOTALL)
    
    return script_cleaned.strip(), imports_str.strip()

def extract_functions(script: str) -> list:
    # Remove everything before the first function definition
    script = re.sub(r'^(.*?)\bdef\b', 'def', script, flags=re.DOTALL)
    
    # Find all function definitions, capturing from one 'def' to the next
    function_pattern = re.compile(r'(def .+?)(?=\ndef |\Z)', re.DOTALL)
    functions = function_pattern.findall(script)
    
    return [func.strip() for func in functions]



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
    parser.add_argument('--program', required=True, type=str, help="Path to the program file")
    parser.add_argument('--precondition', type=str, help="Path to the precondition file")
    parser.add_argument('--postcondition', type=str, help="Path to the postcondition file")
    parser.add_argument('--cex', type=str, help="Output file for the counterexample")

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

    
    # Setup log directory if provided
    # If it is not provided, create the log_temporary directory
    # If the log directory already exists, delete it and recreate it
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
    
    functions_list = extract_functions(cleaned_program)
    postconditions_list =[]
    
    print(f"the imports are {imports}\n")
    for index, func in enumerate(functions_list):
        print(f"Function {index} is: \n{func}\n ")
    
    if config['assessment-mode'] == 'naive':
        return compute_postcondition_naive(description, cleaned_program, config, log_directory)
    # Ensure assessment mode is set to 'postcondition-entailment'
    assert config['assessment-mode'] == 'postcondition-entailment'
    
    # Save the program and description to the log directory
    with (log_directory / str(module_name + '.py')).open("w", encoding="utf-8") as f:
        f.write(program)
    with (log_directory / str(module_name + '_cleaned.py')).open("w", encoding="utf-8") as f:
        f.write(cleaned_program)
    with (log_directory / 'description.txt').open("w", encoding="utf-8") as f:
        f.write(description)
    
    precondition_log_dir = log_directory / 'extract-precondition'
    precondition_log_dir.mkdir()

    postcondition_log_dir = log_directory / 'compute-postcondition'
    postcondition_log_dir.mkdir()
    
    for index, func in enumerate(functions_list):
        # Extract the precondition from the description and program
        
        precondition = extract_precondition(description, imports+'\n'+func, config, precondition_log_dir)
        
        # Save the extracted precondition
        with (log_directory / f'precondition_func_{index}.txt').open("w", encoding="utf-8") as f:
            f.write(precondition)

        # Compute the postcondition from the precondition and program
        # This is where the important work gets done
        postcondition = compute_postcondition(precondition, func, config, postcondition_log_dir)

        # Save the computed postcondition
        with (log_directory / f'postcondition_func_{index}.txt').open("w", encoding="utf-8") as f:
            f.write(postcondition)
        postconditions_list.append(postcondition)


    # Check entailment to verify consistency with the description
    entailment_log_dir = log_directory / 'check_entailment'
    entailment_log_dir.mkdir()
    if len(postconditions_list)==1:
        if cex_path:
            result = check_entailment(description, postcondition, imports + cleaned_program, module_name, config, entailment_log_dir, cex_path)
        else:
            result = check_entailment(description, postcondition, imports + cleaned_program, module_name, config, entailment_log_dir)
    else:
        if cex_path:
            result = check_entailment_mult_func(description, postconditions_list, functions_list, imports, module_name, config, entailment_log_dir, cex_path)
        else:
            result = check_entailment_mult_func(description, postconditions_list, functions_list, imports, module_name, config, entailment_log_dir)

    
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

# Extract the precondition from a description and program using a model
def extract_precondition(description, program, config, log_directory):
    model = get_model(config["model"], config["temperature"], log_directory)
    
    # Use the precondition extractor model to generate the precondition
    return precondition_extractor.default(model, description, program)


# if the assessment mode is set to 'naive', use the naive_question function to compute the postcondition
# we just do an llm call to get if the oce is correct or not using the naive_question function from naive.py
# the prompt and the response from the one API call we are performing are stored in the log dir
def compute_postcondition_naive(description, program, config, log_directory):
    model = get_model(config["model"], config["temperature"], log_directory)
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
def check_entailment(description, postcondition, program, module_name, config, log_directory, cex_path=None):
    model = get_model(config["model"], config["temperature"], log_directory)

    # Perform naive entailment checking, generating counterexamples if necessary
    if config['entailment-mode'] == 'naive':
        if not cex_path:
            correctness = entailment.naive(model, description, postcondition, program, module_name, config)
        else:
            correctness = entailment.naive(model, description, postcondition, program, module_name, config, cex_path)
            if not correctness[0] :
                reason = correctness[1].replace("Correctness: **False**", "")
                cex_generator.output_cex(model, description, postcondition, program, config, cex_path, module_name, reason)
        return correctness[0]

    print(f"Entailment mode {config['entailment-mode']} not supported, only naive is currently implemented")
    raise NotImplementedError

# Check if the postcondition implies compliance with the description using entailment
def check_entailment_mult_func(description, postconditions_list, functions_list, imports, module_name, config, log_directory, cex_path=None):
    model = get_model(config["model"], config["temperature"], log_directory)
    program= imports+"\n"
    total_post=""
    functions =""
    # for func in functions_list:
    #     program += func
    for index, post in enumerate(postconditions_list):
        program += f"#Function {index+1}:\n" + functions_list[index]+"\n\n"
        total_post+= f"Postcondition for function number {index+1} : {post}+\n"
        functions += f"Function number {index+1} :\n Code:\n '''\n{functions_list[index]}\n''' \n\n Output decription for function{index+1}:  {post}\n"
    

    # Perform naive entailment checking, generating counterexamples if necessary
    if config['entailment-mode'] == 'naive':
        if not cex_path:
            correctness = entailment_mult_func.naive_mult_func(model, description, functions, module_name, config)
        else:
            correctness = entailment_mult_func.naive_mult_func(model, description, functions, module_name, config, cex_path)
            if not correctness[0] :
                reason = correctness[1].replace("Correctness: **False**", "")
                cex_generator.output_cex(model, description, total_post, program, config, cex_path, module_name, reason)
        return correctness[0]

    print(f"Entailment mode {config['entailment-mode']} not supported, only naive is currently implemented")
    raise NotImplementedError

# This is just the entry point to the program
if __name__ == "__main__":
    main()
