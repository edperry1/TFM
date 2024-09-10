#!/bin/bash

# Remove carriage return characters from the CaSym.txt file
sed -i 's/\r$//' sralist.txt

# Path to the text file that contains the SRA identifiers
file="sralist.txt"

# Path to the output directory on the hard drive /mnt/d/
output_directory="/home/edperry1/d"

# Check if the output directory exists, if not, create it
if [ ! -d "$output_directory" ]; then
    mkdir -p "$output_directory"
fi

# Iterate over each identifier in the file
while IFS= read -r project; do
    echo "Downloading and converting $project"

    # Download the .SRA file to the output directory
    prefetch -o "${output_directory}/${project}.sra" "$project"

    # Check if the .SRA file was downloaded correctly
    if [ -f "${output_directory}/${project}.sra" ]; then
        echo "${project}.sra file downloaded successfully"

        # Convert the .SRA file to .fastq without compressing them
        fastq-dump --split-files --outdir "$output_directory" "${output_directory}/${project}.sra"

        # Check if the conversion was successful
        if [ $? -eq 0 ]; then
            echo "Conversion of ${project}.sra to .fastq completed"

            # Remove the .SRA file after conversion
            rm "${output_directory}/${project}.sra"
        else
            echo "Error in converting ${project}.sra to .fastq"
        fi
    else
        echo "Error downloading ${project}.sra"
    fi

    echo "Project $project completed"
done < "$file"

echo "Process completed"
