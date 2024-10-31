import re

def remove_imports_and_comments(script: str) -> tuple:
    # Extract import statements
    imports = re.findall(r'^\s*(import .+|from .+ import .+)', script, flags=re.MULTILINE)
    imports_str = "\n".join(imports)
    
    # Remove import statements from the script
    script_no_imports = re.sub(r'^\s*import .*\n?|^\s*from .*\n?', '', script, flags=re.MULTILINE)
    
    # Remove comments (both inline and standalone)
    script_cleaned = re.sub(r'#.*', '', script_no_imports)
    
    return script_cleaned.strip(), imports_str.strip()

def extract_functions(script: str) -> list:
    # Remove everything before the first function definition
    script = re.sub(r'^(.*?)\bdef\b', 'def', script, flags=re.DOTALL)
    
    # Find all function definitions, capturing from one 'def' to the next
    function_pattern = re.compile(r'(def .+?)(?=\ndef |\Z)', re.DOTALL)
    functions = function_pattern.findall(script)
    
    return [func.strip() for func in functions]

script = """
def get_division(number1, number2):
    return number1/number2


def calculate_average(numbers):
    total = 0
    count = 0
    
    
    for num in numbers:
        
        if num > 1:
            total += num
            count += 1
        else:
            print("Skipping non-positive number:", num)

    
    try:
        average = get_division(total,count)
    except ZeroDivisionError:
        average = None  
    
    return average
"""

cleaned_script, imports = remove_imports_and_comments(script)
functions = extract_functions(script)

print("Imports:\n", imports)
print("\nCleaned Script:\n", cleaned_script)
print("\nFunctions List:\n", functions)
print(len(functions))
