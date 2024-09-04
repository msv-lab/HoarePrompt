import os
import re

CEX_GENERATING_PROMPT_TEMPLATE_W = """
You have been assigned the role of a program tester. Now that we know that the given program does not conform to the given problem description, your task is: based on the given program, problem description and the description of the program's output, give a counterexample that demonstrates why the program does not conform to the problem description. You need to strictly follow the format. Follow the following examples:

# Example:

Problem description: Write a python function to count all the substrings starting and ending with same characters.
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

Output description: The function returns the value of the variable 'count', which is equal to the number of times a character at position 'i' in the string 's' is equal to a character at position 'j + 1' for some 'j' in the range '[i, len(s) - 2]'. This implies that 'count' represents the number of consecutive occurrences of identical characters in the string 's' that may form a substring with equal ending and beginning characters, excluding the last character of the string from this comparison.

Explanation: According to the output description, the function returns the value of the variable `count`, which is equal to the number of times a character at position `i` in the string `s` is equal to a character at position `j + 1` for some `j` in the range `[i, len(s) - 2]`. This does not account for substrings of length 1, so it is incorrect.

Correctness: **False**.

Counterexample:
```
from <module_name> import count_Substring_With_Equal_Ends

def test_count_Substring_With_Equal_Ends():
    assert count_Substring_With_Equal_Ends('abba') == 6
```

# Your task:

Problem description: {description}
Program:
```
{program}
```
Output description: {postcondition}
"""


CEX_GENERATING_PROMPT_TEMPLATE_WO = """
You have been assigned the role of a program tester. Now that we know that the given program does not conform to the given problem description, your task is: based on the given program and problem description, give a counterexample that demonstrates why the program does not conform to the problem description. You need to strictly follow the format. Follow the following examples:

# Example:

Problem description: Write a python function to count all the substrings starting and ending with same characters.
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

Output description: The function returns the value of the variable 'count', which is equal to the number of times a character at position 'i' in the string 's' is equal to a character at position 'j + 1' for some 'j' in the range '[i, len(s) - 2]'. This implies that 'count' represents the number of consecutive occurrences of identical characters in the string 's' that may form a substring with equal ending and beginning characters, excluding the last character of the string from this comparison.

Explanation: According to the output description, the function returns the value of the variable `count`, which is equal to the number of times a character at position `i` in the string `s` is equal to a character at position `j + 1` for some `j` in the range `[i, len(s) - 2]`. This does not account for substrings of length 1, so it is incorrect.

Correctness: **False**.

Counterexample:
```
from <module_name> import count_Substring_With_Equal_Ends

def test_count_Substring_With_Equal_Ends():
    assert count_Substring_With_Equal_Ends('abba') == 6
```

# Your task:

Problem description: {description}
Program:
```
{program}
```
"""


def extract_code_blocks(text, module_name):
    pattern = re.compile(r'```(.*?)```', re.DOTALL)
    matches = pattern.findall(text)
    updated_blocks = []
    for code in matches:
        updated_code = re.sub(rf'from\s+<module_name>\s+import', f'from {module_name} import', code)
        updated_blocks.append(updated_code)

    return updated_blocks


def store_cex(response, cex_path, module_name):
    extract_code = extract_code_blocks(response, module_name)
    print(extract_code)

    directory = os.path.dirname(cex_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    with open(cex_path, 'w') as file:
        for idx, code in enumerate(extract_code, start=1):
            file.write(code.strip())
            file.write("\n\n")

def output_cex(model, description, postcondition, program, config, cex_path, module_name):
    if config['cex-mode'] == "with-postcondition":
        prompt = CEX_GENERATING_PROMPT_TEMPLATE_W.format(program=program, description=description,
                                                            postcondition=postcondition)
        response = model.query(prompt)
        print(response)
    elif config['cex-mode'] == "without-postcondition":
        print("----------------yes")
        prompt = CEX_GENERATING_PROMPT_TEMPLATE_WO.format(program=program, description=description)
        response = model.query(prompt)
        print(response)
    else:
        raise NotImplementedError

    store_cex(response, cex_path, module_name)

