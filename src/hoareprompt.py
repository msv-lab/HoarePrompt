import argparse
import json
from pathlib import Path
from model import get_model

import precondition_extractor
import entailment
import comment_style


def main():
    parser = argparse.ArgumentParser(description="HoarePrompt: Structural Reasoning About Programs in Natural Language")
    parser.add_argument('--config', type=str, help="Path to custom configuration file")
    parser.add_argument('--log', type=str, help="Directory to save detailed logs")

    subparsers = parser.add_subparsers(dest='command', help="Available commands")

    assess_parser = subparsers.add_parser('assess', help="Assess if a program is consistent with a description")
    assess_parser.add_argument('--description', type=str, required=True, help="Path to the description file")
    assess_parser.add_argument('--program', type=str, required=True, help="Path to the program file")
    assess_parser.add_argument('--cex', type=str, help="Output file for the counterexample")

    extract_pre_parser = subparsers.add_parser('extract-precondition', help="Extract a precondition from a problem description")
    extract_pre_parser.add_argument('--description', type=str, required=True, help="Path to the description file")
    extract_pre_parser.add_argument('--program', type=str, required=True, help="Program to generate precondition for")

    compute_post_parser = subparsers.add_parser('compute-postcondition', help="Compute a postcondition from a program and a precondition")
    compute_post_parser.add_argument('--precondition', type=str, required=True, help="Path to the precondition file")
    compute_post_parser.add_argument('--program', type=str, required=True, help="Path to the program file")

    assess_parser = subparsers.add_parser('check-entailment', help="Check if the postcondition implies compliance with the problem description")
    assess_parser.add_argument('--description', type=str, required=True, help="Path to the description file")
    assess_parser.add_argument('--program', type=str, required=True, help="Path to the program file")
    assess_parser.add_argument('--postcondition', type=str, required=True, help="Path to the postcondition file")
    assess_parser.add_argument('--cex', type=str, help="Output file for the counterexample")

    args = parser.parse_args()

    if args.config:
        config_file = Path(args.config)
    else:
        config_file = Path("default_config.json")

    with config_file.open() as f:
        config = json.load(f)
    
    log_directory = None
    if args.log:
        log_directory = Path(args.log)
        log_directory.mkdir(parents=True, exist_ok=True)

    if args.command == 'assess':
        with open(args.description, 'r') as f:
            description = f.read()
        with open(args.program, 'r') as f:
            program = f.read()
        assess(description, program, config, log_directory)
    elif args.command == 'extract-precondition':
        with open(args.description, 'r') as f:
            description = f.read()
        with open(args.program, 'r') as f:
            program = f.read()
        return extract_precondition(description, program, config, log_directory)
    elif args.command == 'compute-postcondition':
        with open(args.precondition, 'r') as f:
            precondition = f.read()
        with open(args.program, 'r') as f:
            program = f.read()
        return compute_postcondition(precondition, program, config, log_directory)
    elif args.command == 'check-entailment':
        with open(args.description, 'r') as f:
            description = f.read()
        with open(args.postcondition, 'r') as f:
            postcondition = f.read()
        with open(args.program, 'r') as f:
            program = f.read()
        return check_entailment(description, postcondition, program, config, log_directory)
    else:
        parser.print_help()


def assess(description, program, model, config, log_directory):

    assert config['assessment-mode'] == 'postcondition-entailment'
    
    with (log_directory / 'program.py').open("w", encoding ="utf-8") as f:
        f.write(program)
    with (log_directory / 'description.txt').open("w", encoding ="utf-8") as f:
        f.write(description)

    precondition = extract_precondition(description, program, config, log_directory / 'extract-precondition')
    
    with (log_directory / 'precondition.txt').open("w", encoding ="utf-8") as f:
        f.write(precondition)
    
    postcondition = compute_postcondition(program, precondition, config, log_directory / 'compute-postcondition')

    with (log_directory / 'postcondition.txt').open("w", encoding ="utf-8") as f:
        f.write(postcondition)
    
    postcondition = check_entailment(description, precondition, program, config, log_directory / 'check_entailment')
    

def extract_precondition(description, program, config, log_directory):
    model = get_model(config["model"], config["temperature"], log_directory)

    return precondition_extractor.default(model, description, program)


def compute_postcondition(precondition, program, config, log_directory):
    model = get_model(config["model"], config["temperature"], log_directory)

    if config['postcondition-mode'] == 'hoarecot':
        sp_algorithms = {
            "comment-style": comment_style.compute_postcondition
        }

        sp = sp_algorithms[config['postcondition-cot-prompt']]
        
        return sp(model, precondition, program, config)
    else:
        raise NotImplementedError


def check_entailment(description, postcondition, program, config, log_directory):
    model = get_model(config["model"], config["temperature"], log_directory)

    if config['entailment-mode'] == 'naive':
        entailment.naive(model, description, postcondition, program, config)

    raise NotImplementedError


if __name__ == "__main__":
    main()
