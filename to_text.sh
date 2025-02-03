#!/bin/bash

# =============================================================================
# Script Name: display_all_files_to_txt.sh
# Description: Recursively displays the contents of all files in the
#              'include' and 'src' directories using the `bat` command and
#              saves the output to a specified text file.
# =============================================================================

# ----------------------------- Configuration ----------------------------------

# Define the directories to search

DIRECTORIES=("include" "src" $(pwd) )

# Define the output file (default: all_files_output.txt)
OUTPUT_FILE="all_files_output.txt"

# ------------------------------- Functions ------------------------------------

# Function to check if 'bat' is installed
check_bat_installed() {
    if ! command -v bat &> /dev/null
    then
        echo "Error: 'bat' is not installed on your system."
        echo "Please install 'bat' to use this script. You can install it via Homebrew:"
        echo "  brew install bat"
        exit 1
    fi
}

# Function to initialize the output file
initialize_output_file() {
    echo "Generating documentation of all files in 'include' and 'src' directories..." > "$OUTPUT_FILE"
    echo "==============================================================" >> "$OUTPUT_FILE"
    echo "Output File: $OUTPUT_FILE"
    echo "Generated on: $(date)" >> "$OUTPUT_FILE"
    echo "==============================================================\n" >> "$OUTPUT_FILE"
}

# Function to display files in a given directory and append to the output file
display_files_in_directory() {
    local dir="$1"
    echo "Processing Directory: $dir"

    # Find all regular files in the directory recursively
    find "$dir" -type f | sort | while read -r file; do
        echo "==> ${file} <==" >> "$OUTPUT_FILE"
        #ignore so,jpeg,png,tiff,"TIFF, and build dir"
        if [[ $file == *.pyc ]] ||[[ $file == *.so ]] || [[ $file == *.jpeg ]]|| [[ $file == *.jpg ]] || [[ $file == *.png ]] || [[ $file == *.tiff ]] || [[ $file == *.TIF ]] || [[ $file == *build* ]]|| [[ $file == *.git* ]]|| [[ $file == *algorithms* ]]; then
            continue
        fi

        bat --style=plain "$file" >> "$OUTPUT_FILE" 2>/dev/null
        if [ $? -ne 0 ]; then
            echo "Failed to display file: $file" >> "$OUTPUT_FILE"
        fi
        echo -e "\n--------------------------------------------------------------\n" >> "$OUTPUT_FILE" 
    done
}

write_tree_to_file() {
    #use tree command to write the directory structure to a file
    
    #append the tree to the output file
    echo "==============================================================" >> "$OUTPUT_FILE"
    echo "Directory Structure" >> "$OUTPUT_FILE"
    echo "==============================================================" >> "$OUTPUT_FILE"
    tree -a -I '.git|build|*.png' > "$tree.txt" >> "$OUTPUT_FILE"
    
}
# ------------------------------ Main Script ----------------------------------

# ------------------------------ Main Script ----------------------------------

# Check if 'bat' is installed
check_bat_installed

# Initialize the output file
initialize_output_file

# Iterate over each specified directory
for dir in "${DIRECTORIES[@]}"; do
    if [ -d "$dir" ]; then
        display_files_in_directory "$dir"
    else
        echo "Warning: Directory '$dir' does not exist. Skipping." >> "$OUTPUT_FILE"
    fi
done

write_tree_to_file
echo "All files have been processed and saved to '$OUTPUT_FILE'."

# End of Script