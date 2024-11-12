<table>
  <tr>
    <td style="width: 35%; text-align: center;">
      <img src="./assets/HoarePrompt_logo.png" alt="HoarePrompt Logo" width="100"/>
    </td>
    <td style="width: 65%; text-align: left;">
      <h1>HoarePrompt: Structural Reasoning About Programs in Natural Language</h1>
    </td>
  </tr>
</table>




**HoarePrompt** leverages large language models (LLMs) to perform natural language reasoning about program behavior and correctness. By analyzing programs step-by-step, it generates descriptions of the program's state (i.e., the values of variables) at various points during execution. These descriptions are used to check if the program adheres to a given specification or problem description written in natural language. It is a combination of Chain of thought reasoning and Hoare logic expressed in Natural language to be more easily understood by the LLM. 

HoarePrompt uses different approaches to handle loops and conditional statements, like k-unrolling, improving the accuracy of the description of the states throughout the program execution. If an inconsistency between the program and its specification is found, HoarePrompt not only informs the user that the program is malfunctioning but it is also able to generate a failing test case (counterexample) that demonstrates the error.

## Key Features

1. **Program specification-functionality comparison:** 
   - Verifies if a program is consistent with a natural language description of its behavior (specification).
   - Produces a verdict of `CORRECT` or `INCORRECT`.
   
2. **Precondition and Postcondition Inference:**
   - Extracts preconditions from problem descriptions and computes postconditions for program fragments.
   
3. **Loop Summarization:** 
   - Supports loop unrolling and summarization for better reasoning about loops.

4. **Function functionality extraction**
   - It is capable of extracting and summarizing the functionality of a given function based on its input parameters and output behavior. This helps provide a clearer understanding of the purpose and outcome of the function in natural language.
   
5. **Counterexample Generation:** 
   - Produces counterexamples when a program fails to meet its specification, helping identify the cause of failure.

## Installation

### 1. Set up a Virtual Environment

To ensure dependency isolation and compatibility, it's recommended to create a virtual environment:

```bash
# Create a virtual environment
python3 -m venv hoareprompt-env

# Activate the virtual environment
source hoareprompt-env/bin/activate
```

### 2. Install Dependencies

To get started, install the necessary dependencies by running:

```bash
pip install -r requirements.txt
```

### 3. Set API Keys

Depending on the LLM service you're using, you'll need to set environment variables for the API keys.

For **OpenAI** models:
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

For **Groq** models:
```bash
export GROQ_API_KEY="your-groq-api-key"
```

You can add these export commands to your `.bashrc` or `.zshrc` file to avoid having to set them every time.

## Usage

HoarePrompt provides several commands to analyze programs:

### 1. Assess (default command)

To understand whether a program conforms to a problem description, you can use the following command, as by default, if you run HoarePrompt without specifying a command, it assumes . Here’s how you can use it:

**Command:** `assess`  
**Parameters required:**  
- `--description`: Path to the problem description file  
- `--program`: Path to the program file  
- **Optional**: `--cex` to specify a file for the counterexample if the program is found incorrect.

**Example:**
```bash
python src/hoareprompt.py  --description <FILE> --program <FILE>
or 
python src/hoareprompt.py --command assess --description <FILE> --program <FILE>
```

This will output `CORRECT` or `INCORRECT` depending on the assessment result.
The  command is a combination of the following 3 commands of the HoarePrompt tool, and they are invoked in the order they are presented below.


### 2.Extract Precondition
To get the precondition of the program in the precondition.txt of the log directory

**Command:** `extract-precondition`  
**Parameters required:**  
- `--description`: Path to the problem description file  
- `--program`: Path to the program file  

**Example:**
```bash
python src/hoareprompt.py --command extract-precondition --description example/description.txt --program example/program.py
```

### 3.Compute Postcondition
To get the postcondition of the program in the postcondition.txt of the log directory (but not an assessment of whether the programs follows the specification or not)

**Command:** `compute-postcondition`  
**Parameters required:**  
- `--precondition`: Path to the precondition file  
- `--program`: Path to the program file  

**Example:**
```bash
python src/hoareprompt.py --command compute-postcondition --precondition example/precondition.txt --program example/program.py
```

### 4.Check Entailment

Given a postcondition for a program and a description, it is decided if the program agrees with the specification. Optionally a counter example is generated when the program is incorrect that shows a case when the final state diverges from the specification.
**Command:** `check-entailment`  
**Parameters required:**  
- `--description`: Path to the problem description file  
- `--program`: Path to the program file  
- `--postcondition`: Path to the postcondition file  
- **Optional**: `--cex` to specify a file for the counterexample if the program is incorrect.

**Example:**
```bash
python src/hoareprompt.py --command check-entailment --description example/description.txt --program example/program.py --postcondition example/postcondition.txt
```

### Log and Counterexample Options
#### Log Directory:
You can specify a directory to save detailed logs of the run using the `--log` option.
If the directory already exists it will be overwritten. If no log directory is specified the log_temporary directory will be used (overwritting any previous results there)

**Example:**
```bash
python src/hoareprompt.py --log log1 --program example/program.py --description example/description.txt
```

#### Counterexample (CEX):
Add `--cex <FILE>` to `assess` or `check-entailment` commands to generate a counterexample when the program is incorrect.

**Example:**
```bash
python src/hoareprompt.py --command assess --program example/program.py --description example/description.txt --cex example/test.py
```



## Interface Changes and Enhanced Functionality

Recent updates to HoarePrompt have streamlined the command-line interface and added flexibility:

- **Argument Flexibility:** 
  Command-line arguments for all commands can now be supplied in any order, allowing more flexibility in usage.
  
- **Logging Directory Behavior:** 
  If no log directory is specified, a temporary directory (`log_temporary`) is created automatically. If the directory exists, it is recreated to ensure a clean logging environment.

## Example

To run an example, use:

```bash
python src/hoareprompt.py  --program example/program.py --description example/description.txt --log log_001
```

This will store logs in `log_001`. If you also want to generate a counterexample:

```bash
python src/hoareprompt.py --command assess --program example/program.py --description example/description.txt  --log log_001 --cex example/test.py 
```

The generated counterexample will be saved to  `example/test.py` and in the log directory as  `test.py`. You can run it with:

```bash
./src/run_tests.sh example/test.py
```

## Configuration

HoarePrompt allows users to configure its behavior through a JSON configuration file. By default, it uses `default-config.json`, but you can specify a custom config with:

```bash
python src/hoareprompt.py --config <FILE>
```
 Normally we suggest using  default-config.json for normal HoarePrompt operations. Additionally, for a simpler, naive approach to verification, config_naive.json is available, which performs a single api call to the LLM.This is our baseline.

### Assessment Modes
The assessment-mode parameter controls the approach HoarePrompt uses to verify code correctness. The following modes are available:

#### naive: In this mode, the tool directly assesses if the program aligns with its description without detailed structural analysis.

Few-Shot Learning (fsl): When using the naive assessment mode, you can optionally enable Few-Shot Learning (FSL) by setting the fsl parameter in the configuration file:
  fsl: true (default): Provides the model with examples to improve reasoning and accuracy.
  fsl: false: Disables few-shot learning, using a simpler prompt structure.
If the fsl parameter is omitted, it defaults to true.
#### postcondition-entailment: This mode uses postcondition analysis to determine if the program's behavior meets its specification.

Annotated Mode (annotated): When using the postcondition-entailment mode, you can enable annotated mode by setting annotated in the configuration:
  annotated: true: Uses the annotated code tree, which includes a detailed structure of postconditions and state changes, for entailment checking.
  annotated: false (default): Uses the standard program code and computed functionality for entailment checking.
If the annotated parameter is omitted, it defaults to false.

### Main Configuration Options:

- **model**: Choose the model to use. Supported models can be found in `src/model.py`.
- **temperature**: Control the randomness of the model's outputs.
- **assessment-mode**:
  - `naive`: Directly ask the model for the correctness of the program.
  - `postcondition-entailment`: Compute postcondition and check entailment based on precondition and program.
- **postcondition-mode**:
  - `one-step`: Compute the postcondition in one step.
  - `hoarecot`: Use a Chain-of-Thought (CoT) method to compute the postcondition step-by-step.
- **postcondition-cot-prompt**:
  - `comment-style`: State descriptions are embedded in comments within the program code.
  - `node-based-style`: Use Hoare logic premises as few-shot examples for generating postconditions.
- **loop-unrolling-count**: Number of times to unroll loops during analysis (set to `0` to disable loop summarization).
- **entailment-mode**:
  - `naive`: Directly ask the model if the postcondition satisfies the problem description.
  - `cot`: Use a Chain-of-Thought (CoT) approach to analyze entailment. IT HAS NOT BEEN DEVELOPED YET
- **cex-mode**:
  - `without-postcondition`: Generate a counterexample based on the program and problem description only.
  - `with-postcondition`: Generate a counterexample based on the program, description, and inferred postcondition.
- **fsl**: Only to be used in combination with assesment mode: naive
  - `True`: The default option. It uses few shot learning in the entailement.
  - `False`: It does not use few shot learning in the entailement.
- **annotated**: Only to be used in combination with assesment mode: naive
  - `True`:  It uses the the annotated code tree in the entailement.
  - `False`: The default option. It uses the original code plus the calculated functionality in the entailement.
  
## Implementation Details

HoarePrompt's reasoning process revolves around breaking down programs into smaller components and analyzing the behavior of each component in isolation:
- **Precondition Extraction**: The tool generates a precondition based on the natural language description and the program itself.
- **Postcondition Computation**: The postcondition is inferred by simulating the execution of the program step-by-step.
- **Loop Unrolling**: Loops are handled via k-unrolling (simulating the first k iterations) to better understand how the loop transforms variables. In more detail or for loops are transformed into while loops and unrolled with an unrolling factor k as specified in the configuration json.
- **Function summarising**: The functionality of a function can be summarised to assist the LLM into infering about the states after its execution 
- **Entailment Checking**: The postcondition is checked to determine whether it meets the requirements described in the natural language specification.

For more complex control structures, such as conditionals (`if` statements) and exception handling (`try-except` blocks), HoarePrompt generates specialized prompts for the model, ensuring the correct reasoning is applied to those cases. 

## Contributions
This is a project of Peking Univeristy. Feel free to contribute to HoarePrompt-data by opening issues or submitting pull requests on GitHub. Your contributions are highly appreciated!

<div style="display: flex; justify-content: center;">
  <table style="table-layout: fixed; text-align: center;">
    <tr>
      <td style="width: 50%; text-align: center;">
        <img src="./assets/PKU.png" alt="Image 1" width="300"/>
      </td>
      <td style="width: 50%; text-align: center;">
        <img src="./assets/HoarePrompt_logo.png" alt="Image 2" width="300"/>
      </td>
    </tr>
  </table>
</div>