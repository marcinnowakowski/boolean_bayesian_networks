#!/bin/bash

# Create output directory for SIF results_20_01
mkdir -p output/results_20_01

echo "Starting BNFinder analysis on files in output/bnfinder_input/..."

# Loop through all .txt files in the input directory
for f in output/bnfinder_input/*.txt; do
    if [ -f "$f" ]; then
        filename=$(basename "$f")
        name_no_ext="${filename%.*}"
        
        echo "----------------------------------------------------------------"
        echo "Processing $filename"
        echo "----------------------------------------------------------------"
        
        # Run BNFinder via Docker
        # -v "$(pwd)":/data  : Mounts the current project directory to /data in the container
        # -e ...             : Input file path (inside container)
        # -n ...             : Output network file path (inside container)
        # -g                 : Allow self-loops (CRITICAL for this network)
        # -v                 : Verbose mode
        docker run --rm -v "$(pwd)":/data bnfinder bnf \
            -e "/data/output/bnfinder_input/$filename" \
            -n "/data/output/results/${name_no_ext}.sif" \
            -g \
            -v
    fi
done

echo "----------------------------------------------------------------"
echo "Analysis complete. Results are in output/results/"
