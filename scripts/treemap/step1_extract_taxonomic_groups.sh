#!/bin/bash

# Check if input file is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <input_file>"
    exit 1
fi

input_file="$1"
output_file="taxonomy_counts.txt"

# Extract the fourth taxonomic group and count occurrences
awk -F'|' '{split($4, a, ";"); if (length(a) >= 4) print a[4]}' "$input_file" | sort | uniq -c | sort -nr
