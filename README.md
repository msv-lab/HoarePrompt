# HoarePrompt: Structural Reasoning About Programs in Natural Language

HoarePrompt reasons about programs in natural languages using LLMs. It analyses a given program step-by-step by inferring natural language descriptions of states (values of program variables) that the program can reach during execution at various program locations. To enhance precision of these descriptions, HoarePrompt uses a special technique to summarise loops. These descriptions are then applied to assess the correctness of this program with respect to a specification written in natural language. When the program is deemed incorrect, HoarePrompt generates a failing test acting as a counterexample of the program's compliance with the natural language specification.

## Installation

In your virtual environment, install dependencies specified in the requirement file:

    pip install -r requirements.txt
    
Depending on the used LLM, define environment variables holding API keys, `OPENAI_API_KEY` or `GROQ_API_KEY`.

## Usage

HoarePrompt's key feature is assessing if a given implementation is consistent with a given problem description. It can be executed as 

    python hoareprompt.py assess --description <FILE> --program <FILE>
    
HoarePrompt also provides commands to run intermediate assessment steps. This is to extract a precondition from a problem description:

    python hoareprompt.py extract-pre --description <FILE> --output <FILE>
        
This is to compute a postcondition, given a program and a precondition:

    python hoareprompt.py compute-post --precondition <FILE> --program <FILE> 

This is to assess if a program is consistent with a program description based on the inferred postcondition:

    python hoareprompt.py assess --description <FILE> --postcondition <FILE> --program <FILE> 

Adding `--cex <FILE>` to the last command will also output a counterexample.

## Configuration

By default, HoarePrompt uses configuration options specified in "default-config.json". A custom config can be supplied using the option `--config <FILE>`. There are the main supported options:

- `model`
- `temperature`
- `context-in-prompt`: how code context is represented in the prompt, can be either `comment-style` or `few-shot-style`
- `loop-unrolling-count`: how many time the loops are unrolled during analysis. `0` disables loop summarisation.

## Limitations
