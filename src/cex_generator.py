import os
import re

# This function returns a template for instructing the model to generate a counterexample.
# If the 'use_postcondition' flag is True, it includes a description of the actual program's output in the template.

def cex_generation_instruction(use_postcondition):
   TEMPLATE = """
The program below is incorrect. Given the program, a description of the problem the program is intended to solve{optional_postcondition}, generate a counterexample test that demonstrates the discrepancy between the expected and the actual outputs. Explain how this test demonstrates the discrepancy. The provided incorrect program must fail this test. The test must import the tested function from the placeholder <module_name>.
"""
   if use_postcondition:
       return TEMPLATE.format(optional_postcondition=", and a description of the actual program's output")
   else:
       return TEMPLATE.format("")

# This function provides an example of a counterexample generation.
# It includes both the incorrect program and the counterexample test.
# If 'use_postcondition' is True, it includes the output description.
def cex_generation_example(use_postcondition):
    PROGRAM = """
Problem description: Write a Python function to count all the substrings starting and ending with same characters.

Program:
```
def count_Substring_With_Equal_Ends(s):
    count = 0
    for i in range(len(s)-1):
        for j in range(i,len(s)-1):
            if s[i] == s[j+1]:
                count += 1
    return count
```
"""
    OUTPUT_DESCRIPTION_AND_EXPLANATION = """
Output description: The function returns the value of the variable 'count', which is equal to the number of times a character at position 'i' in the string 's' is equal to a character at position 'j + 1' for some 'j' in the range '[i, len(s) - 2]'. This implies that 'count' represents the number of consecutive occurrences of identical characters in the string 's' that may form a substring with equal ending and beginning characters, excluding the last character of the string from this comparison.

Explanation: According to the output description, the function does not account for substrings of length 1, so it is incorrect. Thus, for the 'abba' it will return 2 ('bb' and 'abba'), while the expected output is 6 ('a', 'b', 'b', 'a', 'bb' and 'abba').
"""

    ONLY_EXPLANATION = """
Explanation: The function does not account for substrings of length 1, so it is incorrect. Thus, for the 'abba' it will return 2 ('bb' and 'abba'), while the expected output is 6 ('a', 'b', 'b', 'a', 'bb' and 'abba').
"""

    COUNTEREXAMPLE="""
Counterexample test (note the placeholder <module_name>):
```
from <module_name> import count_Substring_With_Equal_Ends

def test_count_Substring_With_Equal_Ends():
    assert count_Substring_With_Equal_Ends('abba') == 6
```
"""
    if use_postcondition:
        return PROGRAM + OUTPUT_DESCRIPTION_AND_EXPLANATION + COUNTEREXAMPLE
    else:
        return PROGRAM + ONLY_EXPLANATION + COUNTEREXAMPLE

# This function generates a template for the counterexample generation prompt.
# It includes the instruction and an example, followed by a task specific to the given problem.
def cex_generation_prompt_template(use_postcondition, reason):
    HEADER_TEMPLATE = """
{instruction}

Follow the format in these examples:

# Example 1

{example}
"""
    TASK_TEMPLATE = """
# Your task

Problem description: {description}

Program:
```
{program}
```
"""
    if use_postcondition:
        TASK_TEMPLATE += "Output description: {postcondition} \n And the explanation of the output: {reason}"

    header = HEADER_TEMPLATE.format(instruction=cex_generation_instruction(use_postcondition),
                                    example=cex_generation_example(use_postcondition))
    return header + TASK_TEMPLATE
    
# This function extracts code blocks  from the model's response.
# It replaces the placeholder <module_name> with the actual module name provided.
def extract_code_blocks(text, module_name):
    pattern = re.compile(r'```python(.*?)```', re.DOTALL)
    matches = pattern.findall(text)
    if not matches:
        pattern = re.compile(r'```(.*?)```', re.DOTALL)
        matches = pattern.findall(text)
    if not matches:
        print("No code blocks found in the cex response.")
    updated_blocks = []
    for code in matches:
        updated_code = re.sub(rf'from\s+<module_name>\s+import', f'from {module_name} import', code)
        updated_blocks.append(updated_code)

    return updated_blocks

# This function stores the generated counterexample into a file.
# It ensures that the necessary directories exist and writes the extracted code to the specified path.
def store_cex(response, cex_path, module_name):
    extract_code = extract_code_blocks(response, module_name)
    

    directory = os.path.dirname(cex_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    with open(cex_path, 'w') as file:
        for idx, code in enumerate(extract_code, start=1):
            file.write(code.strip())
            file.write("\n\n")

# This is the main function that interacts with the model to generate the counterexample.
# It selects the appropriate prompt template, with or without postcondition, dpending on the input param, and stores the generated counterexample.
def output_cex(model, description, postcondition, program, config, cex_path, module_name, reason):
    if config['cex-mode'] == "with-postcondition":
        template = cex_generation_prompt_template(True, reason)
    elif config['cex-mode'] == "without-postcondition":
        template = cex_generation_prompt_template(False, reason)
    else:
        raise NotImplementedError
    prompt = template.format(program=program,
                             description=description,
                             postcondition=postcondition,
                             reason=reason)
    response = model.query(prompt)
   
    
    store_cex(response, cex_path, module_name)

