#!/bin/bash

# Check if the correct number of arguments is provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 input_file output_file"
    exit 1
fi

# Input and output file names from arguments
input_file="$1"
output_file="$2"

# Add header to CSV
echo "Count,Taxonomic Group" > "$output_file"

# Read the input file and append formatted lines to the CSV file
while read -r line; do
    count=$(echo "$line" | awk '{print $1}')
    group=$(echo "$line" | awk '{$1=""; print substr($0,2)}')  # Remove leading space
    echo "$count,$group" >> "$output_file"
done < "$input_file"

echo "Data has been processed and saved to $output_file."
