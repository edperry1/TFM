#!/usr/bin/python

import sys
import csv
import os
import glob
import shutil
import subprocess


# Define the path to the CSV file containing SRR codes and directory names.
sra_csv_path = "./srr.csv"


# Function to run a shell command and log the output to a file.
def run_command(command, logfile_handel):
    print("\n", command)
    print("\n", command, file=logfile_handel)
    result = subprocess.run(command.split(), capture_output=True, text=True)
    print(result.stdout)
    print(result.stdout, file=logfile_handel)
    if result.returncode != 0:
        print("Count not run the command")
        print(result.stderr)
        print(result.stderr, file=logfile_handel)
        exit(1)


# Retrieve the SRR code passed as a command-line argument.
code = sys.argv[1]

# Dictionary to map SRR codes to directory names.
srr_dirnames = {}

# Open and read the CSV file.
with open(sra_csv_path) as f:
    f.readline() # Skip the header line.
    csv_data = csv.reader(f)
# Iterate through each row in the CSV file.
    for i in csv_data:
        srr_code = i[0].strip() # Extract and clean the SRR code.
        filename = i[1].replace(" ", "").replace("\t", "") # Clean the directory name.
        if(len(srr_code) > 5 and len(filename)>5): # Only consider valid entries.
            srr_dirnames[srr_code] = filename # Map the SRR code to the directory


# Check if the provided SRR code exists in the CSV file.
if code not in srr_dirnames:
    print(f"Could not find Directory name for code: {code} in the csv file", file=sys.stderr)
    exit(1) # Exit if the code is not found.


# Find all fastq files related to the SRR code in the current directory.
fasq_files = [f for f in glob.glob(f"{code}*") if os.path.isfile(f)]
# Ensure there are exactly two fastq files (paired-end data).
if len(fasq_files) != 2:
    print(f"Could not find fastq files for code: {code} in the current Directory", file=sys.stderr)
    exit(1)

# Sort the fastq files so that _1 and _2 files are in the correct order.
fasq_files.sort(key=lambda x: int(x.split(".")[0][-1]))

# Retrieve the corresponding directory name from the dictionary.
dir_name = srr_dirnames[code]
os.makedirs(dir_name, exist_ok=True) # Create the directory if it doesn't exist.
for file in fasq_files: # Move the fastq files into the created directory.
    shutil.move(file, dir_name)

# Open a log file in the directory to record command outputs.
log_file = open(f"{dir_name}/logfile.txt", "w")

# Run FastQC quality checks on the raw fastq files.
fastqc_command = f"fastqc {dir_name}/{fasq_files[0]} {dir_name}/{fasq_files[1]} -o {dir_name}"
run_command(fastqc_command, log_file)

# Define paths for the trimmed fastq files.
trim_fasq_1 = [f"{dir_name}/{code}_1_paired_trimmed.fastq", f"{dir_name}/{code}_1_unpaired.fastq"]
trim_fasq_2 = [f"{dir_name}/{code}_2_paired_trimmed.fastq", f"{dir_name}/{code}_2_unpaired.fastq"]

# Run Trimmomatic to trim adapters and low-quality sequences.
trimomatic_command = f"trimmomatic PE -phred33 {dir_name}/{fasq_files[0]} {dir_name}/{fasq_files[1]} {trim_fasq_1[0]} {trim_fasq_1[1]} {trim_fasq_2[0]} {trim_fasq_2[1]} ILLUMINACLIP:NexteraXT_adapters.fa:2:30:10  LEADING:5 TRAILING:5 SLIDINGWINDOW:4:15 MINLEN:50"
run_command(trimomatic_command, log_file)

# Run FastQC on the trimmed paired-end files to assess quality after trimming.
fastqc_command = f"fastqc {trim_fasq_1[0]} {trim_fasq_2[0]} -o {dir_name}"
run_command(fastqc_command, log_file)


# Run MEGAHIT to perform de novo assembly on the trimmed fastq files.
megahit_command = f"megahit -1 {trim_fasq_1[0]} -2 {trim_fasq_2[0]} -o {dir_name}/megahit_output_{code} -t 16"
run_command(megahit_command, log_file)

# Run BLASTN to search for matches in a custom rRNA operons database.
blastn_command = f"blastn -query {dir_name}/megahit_output_{code}/final.contigs.fa -db database/Blast/customdb/custom_rrna_operons_db -out {dir_name}/results.txt -evalue 1e-10 -num_threads 8 -outfmt 6"
run_command(blastn_command, log_file)

# Use AWK to filter BLAST results based on alignment length and percentage identity.
awk_command = f"awk '$4 >= 120 && $3 > 95' {dir_name}/results.txt > {dir_name}/results.txt"
run_command(awk_command, log_file)

# Use AWK to extract unique counts of a specific column (column 2) from the filtered BLAST results.
awk_command = f"awk '{{print $2}}' {dir_name}/results.txt | sort | uniq -c | sort -nr > {dir_name}/unique_column2_counts.txt"
run_command(awk_command, log_file)

# Generate a CSV file from the unique counts extracted in the previous step.
print("\nproducing unique.csv")
file = open(f"{dir_name}/unique_column2_counts.txt")
out = open(f"{dir_name}/unique.csv", "w")
for line in file:
    splitted = line.split("|")
    print(",".join(splitted[0].strip().split()), end=",", file=out)
    print(",".join(splitted[-1].strip().split(";")), file=out)
file.close()
out.close()

# Cleanup: Remove all fastq files in the directory.
cleanup_command = f"rm -r {dir_name}/*.fastq"
run_command(awk_command, log_file)

# Cleanup: Remove all zip files in the directory (usually from FastQC results).
cleanup_command = f"rm -r {dir_name}/*.zip"
run_command(awk_command, log_file)
