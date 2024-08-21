import argparse
import json
from pathlib import Path
from model import get_model


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
    extract_pre_parser.add_argument('--output', type=str, required=True, help="Output file for the precondition")

    compute_post_parser = subparsers.add_parser('compute-postcondition', help="Compute a postcondition from a program and a precondition")
    compute_post_parser.add_argument('--precondition', type=str, required=True, help="Path to the precondition file")
    compute_post_parser.add_argument('--program', type=str, required=True, help="Path to the program file")

    assess_parser = subparsers.add_parser('check-entailment', help="Check if the postcondition implies compliance with the problem description")
    assess_parser.add_argument('--description', type=str, required=True, help="Path to the description file")
    assess_parser.add_argument('--program', type=str, required=True, help="Path to the program file")
    assess_parser.add_argument('--postcondition', type=str, required=True, help="Path to the postcondition file")
    assess_parser.add_argument('--cex', type=str, help="Output file for the counterexample")

    # Parse the arguments
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

    model = get_model(config["model"], config["temperature"])

    if args.command == 'assess':
        with open(args.description, 'r') as f:
            description = f.read()
        with open(args.program, 'r') as f:
            program = f.read()
        assess(description, program, config, log_directory)
    elif args.command == 'extract-precondition':
        extract_precondition(args, config, log_directory)
    elif args.command == 'compute-postcondition':
        compute_postcondition(args, config, log_directory)
    elif args.command == 'check-entailment':
        check_entailment(args, config, log_directory)
    else:
        parser.print_help()


def assess(description, program, model, config):
    extract_precondition(, config, log_directory)


def extract_precondition(description, config, model, config):


def compute_postcondition(args, model, config):


def check_entailment(args, model, config):    


if __name__ == "__main__":
    main()

