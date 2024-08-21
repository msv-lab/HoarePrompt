# HoarePrompt: Structural Reasoning About Programs in Natural Language

HoarePrompt reasons about programs in natural languages using LLMs. It analyses a given program step-by-step by inferring natural language descriptions of states (values of program variables) that the program can reach during execution at various program locations. To enhance precision of these descriptions, HoarePrompt uses a special technique to summarise loops. These descriptions are then applied to assess the correctness of this program with respect to a specification written in natural language. When the program is deemed incorrect, HoarePrompt generates a failing test acting as a counterexample of the program's compliance with the natural language specification.

## Installation

In your virtual environment, install dependencies specified in the requirement file:

    pip install -r requirements.txt
    
Depending on the used LLM, define environment variables holding API keys, `OPENAI_API_KEY` or `GROQ_API_KEY`.

## Usage

HoarePrompt's key feature is assessing if a given implementation is consistent with a given problem description. It can be done by executing the command

    python hoareprompt.py classify --description <FILE> --program <FILE>
    
that prints either `CORRECT` or `INCORRECT` on STDOUT.
    
HoarePrompt also provides commands to run intermediate assessment steps. This is to extract a precondition from a problem description (printed on STDOUT):

    python hoareprompt.py extract-precondition --description <FILE>
        
This is to compute a postcondition, given a program and a precondition:

    python hoareprompt.py compute-postcondition --precondition <FILE> --program <FILE> 

This is to assess if a program is consistent with a program description based on the inferred postcondition:

    python hoareprompt.py check-entailment --description <FILE> --postcondition <FILE> --program <FILE> 

Adding `--cex <FILE>` to `assess` or `check-entailment` commands will also output a counterexample.

Adding `--log <DIR>` to any of these commands saves detailed logs in the specified directory.

## Configuration

By default, HoarePrompt uses configuration options specified in "default-config.json". A custom config can be supplied using the option `--config <FILE>`. There are the main supported options:

- `model`: check `src/model.py` for supported models
- `temperature`
- `classification-mode`:
  - `naive`: directly ask the model
  - `zero-shot-cot`: ask to reason step-by-step
  - `postcondition-entailment`: compute postcondition and check entailment
- `postcondition-mode`:
  - `one-step`: compute postcondition in one step
  - `cot`: compute postcondition in step-by-step
- `postcondition-cot-prompt`:
  - `comment-style`: state description is embedded in comments
  - `few-shot-style`: Hoare logic premises are used as few-shot examples
- `loop-unrolling-count`: how many times the loops are unrolled during analysis. `0` disables loop summarisation.
- `entailment-mode`:
  - `naive`: directly ask the model
  - `cot`: a CoT prompt to analyse the postcondition

## Limitations
