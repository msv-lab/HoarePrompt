import re
import subprocess
import os

PROMPT = """
Your task is to determine if a given Python program is correct based on the provided problem description. Assume valid inputs as described in the problem description.

# Problem:
{description}

# Program:
{code}

If the program is correct:
# Your response (please strictly follow the format below):
Correctness: **True**

If the program is incorrect:
# Your response:
Correctness: **False**
Counterexample test (additionally provide a counterexample strictly following the format below and make sure the input and output formats meet the problem requirements):
Input: 
```

```
Expected Output: 
```

```
"""

PROMPT_COMPLEX = """
**Role**: As a tester, your task is to create comprehensive test cases for the following coding problem. These test cases should encompass Basic and Edge scenarios to ensure the code's robustness, reliability, and scalability.

**Problem Description**:
{description}

**1. Basic Test Cases**:
- **Objective**: To verify the fundamental functionality of the `has_close_elements` function under normal conditions.

**2. Edge Test Cases**:
- **Objective**: To evaluate the function's behavior under extreme or unusual conditions.

**Instructions**:
- Implement a comprehensive set of test cases following the guidelines above.
- Ensure each test case is complete (no omission) and well-documented with comments explaining the scenario it covers.
- Pay special attention to edge cases as they often reveal hidden bugs.
- Do not repeat, do not summarize.

All test cases you give need to strictly follow the problem description and format like this:
# Test 1
**Input**: 
```

```
**Output**: 
```

```
"""


def extract_input_and_expected(test_str):
    input_pattern = re.compile(r'Input:\s*```\s*(.*?)\s*```', re.DOTALL)
    expected_pattern = re.compile(r'Expected Output:\s*```\s*(.*?)\s*```', re.DOTALL)

    input_match = input_pattern.search(test_str)
    expected_match = expected_pattern.search(test_str)

    if input_match and expected_match:
        input_str = input_match.group(1).strip()
        expected_str = expected_match.group(1).strip()
        return input_str, expected_str, True
    else:
        return None, None, False


def extract_result(s: str, keyword: str):
    pattern = fr"{keyword}:\s*\*\*(.*?)\*\*"
    matches = re.findall(pattern, s, re.DOTALL)
    if matches:
        # Select the last match
        res = matches[-1]
        # Clean up the beginning and end of the string for any weird characters like * or newlines
        return res.strip(), True
    return s, False


def verify_program_output(code, input_data, expected_output):
    """
    Function to verify if the program's output matches the expected output.

    Parameters:
    - code: str, The python code as a string.
    - input_data: str, The input data to be passed to the program.
    - expected_output: str, The expected output that the program should produce.

    Returns:
    - True if the output matches, False otherwise.
    """

    # Write the code to a temporary Python file
    temp_file_path = "temp_program.py"
    with open(temp_file_path, "w") as temp_file:
        temp_file.write(code)

    # Run the program with the provided input and capture the output
    process = subprocess.Popen(
        ['python3', temp_file_path],  # Run the program using Python
        stdin=subprocess.PIPE,  # Provide input to the program via stdin
        stdout=subprocess.PIPE,  # Capture the output from stdout
        stderr=subprocess.PIPE  # Capture any errors (if any)
    )

    # Send input_data to the program and get the output
    output, error = process.communicate(input=input_data.encode())

    # Decode the output to string
    output = output.decode().strip()

    # Delete the temporary file after the program runs
    os.remove(temp_file_path)

    print("-" * 50)

    print("actual output:\n" + output)

    print("expected output:\n" + expected_output)

    print("-" * 50)

    # Check if the output matches the expected output
    return output == expected_output


def naive_test(description, code, model, retry=True):
    prompt = PROMPT.format(description=description, code=code)
    response = model.query(prompt)
    print(response)
    post, found = extract_result(response, "Correctness")
    print("*" * 50)
    print(f"{description} \n {code}")
    print(f"LLM Reply: {post}")
    if retry and not found:
        return naive_test(description, code, model, retry=False)
    if 'true' in post.lower().strip():
        return True
    if "false" in post.lower().strip():
        return False
    return post


def naive_test_verify_ans(description, code, original_code, model, retry=True):
    prompt = PROMPT.format(description=description, code=code)
    response = model.query(prompt)
    print(response)
    post, found = extract_result(response, "Correctness")
    print("*" * 50)
    print(f"{description} \n {code}")
    print(f"LLM Reply: {post}")
    if retry and not found:
        return naive_test_verify_ans(description, code, original_code, model, retry=False)
    if 'true' in post.lower().strip():
        return True
    if "false" in post.lower().strip():
        test_input, test_expected, test_found = extract_input_and_expected(response)
        if retry and not test_found:
            print("Test not found: Retry")
            return naive_test_verify_ans(description, code, original_code, model, retry=True)
        if verify_program_output(original_code, test_input, test_expected):
            print("Test Reply: test_passed, the answer changes to True")
            return True
        else:
            print("Test Reply: test_failed, the answer remains False")
            return False
    return post


def extract_input_output(text):
    input_pattern = r'\*\*Input\*\*:\s*```\s*(.*?)\s*```'
    output_pattern = r'\*\*Output\*\*:\s*```\s*(.*?)\s*```'

    inputs = re.findall(input_pattern, text, re.DOTALL)
    outputs = re.findall(output_pattern, text, re.DOTALL)

    # 将匹配到的内容打印出来
    input_output_pairs = []
    for i, input_data in enumerate(inputs):
        # 提取对应的output
        output_data = outputs[i] if i < len(outputs) else ""
        input_output_pairs.append((input_data.strip(), output_data.strip()))

    return input_output_pairs


def test_agentcoder(description, code, original_code, model, retry=True):
    prompt = PROMPT_COMPLEX.format(description=description, code=code)
    response = model.query(prompt)
    print(response)

    input_output_pairs = extract_input_output(response)
    if not input_output_pairs:
        test_agentcoder(description, code, original_code, model, retry=True)

    test_number = 0
    correctness = True

    for idx, (input_data, output_data) in enumerate(input_output_pairs, start=1):
        test_number += 1
        print(f"Test Case {idx}:")
        print(f"Input:\n{input_data}")
        print(f"Output:\n{output_data}")
        result = verify_program_output(original_code, input_data, output_data)
        if not result:
            correctness = False
        print(result)
        print("-" * 50)
        if test_number > 20:
            break
    print(f"Test Result: {correctness}")
    return correctness