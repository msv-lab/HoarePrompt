import argparse
import shutil
import json
import os
from pathlib import Path
from model import get_model

import precondition_extractor
import entailment
import comment_style
import node_base_style.complete
import cex_generator


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

    # I also want to store the config file in the log directory
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
        return extract_precondition(description, program, config, log_directory)
    
    # Handle the 'compute-postcondition' command
    elif args.command == 'compute-postcondition':
        if not args.precondition or not args.program:
            raise ValueError("Both --precondition and --program must be provided for the 'compute-postcondition' command.")
        with open(args.precondition, 'r') as f:
            precondition = f.read()
        with open(args.program, 'r') as f:
            program = f.read()
        return compute_postcondition(precondition, program, config, log_directory)
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
        return check_entailment(description, postcondition, program, module_name, config, log_directory, cex_path)
    # If no command is provided, display help information
    else:
        parser.print_help()

# Assess if a program is consistent with the description using pre/postconditions and entailment checking
def assess(description, program, module_name, config, log_directory, cex_path):

    # Ensure assessment mode is set to 'postcondition-entailment'
    assert config['assessment-mode'] == 'postcondition-entailment'
    
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

    # Compute the postcondition from the precondition and program
    # This is where the important work gets done
    postcondition_log_dir = log_directory / 'compute-postcondition'
    postcondition_log_dir.mkdir()
    postcondition = compute_postcondition(precondition, program, config, postcondition_log_dir)

    # Save the computed postcondition
    with (log_directory / 'postcondition.txt').open("w", encoding="utf-8") as f:
        f.write(postcondition)

    # Check entailment to verify consistency with the description
    entailment_log_dir = log_directory / 'check_entailment'
    entailment_log_dir.mkdir()
    if cex_path:
        result = check_entailment(description, postcondition, program, module_name, config, entailment_log_dir, cex_path)
    else:
        result = check_entailment(description, postcondition, program, module_name, config, entailment_log_dir)
    
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
            if correctness is False:
                cex_generator.output_cex(model, description, postcondition, program, config, cex_path, module_name)
        return correctness

    print(f"Entailment mode {config['entailment-mode']} not supported, only naive is currently implemented")
    raise NotImplementedError

# This is just the entry point to the program
if __name__ == "__main__":
    main()
