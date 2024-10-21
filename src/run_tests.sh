#!/bin/bash

# Check if a file path is provided as an argument
if [ -z "$1" ]; then
  echo "Usage: $0 /path/to/your/test_file.py"
  exit 1
fi

# Get the directory of the provided file path
file_path="$1"
directory=$(dirname "$file_path")
file_name=$(basename "$file_path")

# Path to the source file you want to copy (adjust as needed)
source_file="src/run_tests.py"

# Copy the source file to the target directory
cp "$source_file" "$directory"

cd "$directory"

# Execute the copied run_tests.py with the original file path as argument
python "run_tests.py" "$file_name"

rm -rf "run_tests.py"
