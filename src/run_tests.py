import importlib.util
import inspect
import sys
import argparse
import os

def run_functions_in_file(file_path):
    # Load the module from the file
    module_name = "dynamic_module"
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

     # Get the absolute path of the file for comparison
    module_file_path = os.path.abspath(file_path)

    # Iterate through all objects in the module to find functions defined in this file
    functions = [
        func for name, func in inspect.getmembers(module, inspect.isfunction)
        if inspect.getsourcefile(func) == module_file_path
    ]

    # Execute each function found
    for func in functions:
        print(f"Executing {func.__name__}...")
        try:
            func()
        #in the case of assertion error, print the error message
        except AssertionError as e:
            print(f"The test case had an assertion error for {func.__name__}")
        except Exception as e:
            print(f"The test case failed for {func.__name__}: {e}")

if __name__ == "__main__":
    # Parse the command-line argument for the file path
    parser = argparse.ArgumentParser(description="Run all functions in a Python file.")
    parser.add_argument("file_path", type=str, help="Path to the Python file")
    args = parser.parse_args()

    run_functions_in_file(args.file_path)
