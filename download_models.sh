#!/bin/bash

# Create models directory if it doesn't exist
mkdir -p models

# Base URL for the files
BASE_URL="http://basalt.amulet.cs.cmu.edu/screen2vec"

# Array of filenames to download
FILES=(
    "visual_encoder.ep800"
    "layout_encoder.ep800"
    "UI2Vec_model.ep120"
    "Screen2Vec_model_v4.ep120"
)

echo "Starting download of model files..."

# Download each file
for file in "${FILES[@]}"; do
    echo "Downloading $file..."
    if curl -L -o "models/$file" "$BASE_URL/$file"; then
        echo "✓ Successfully downloaded $file"
    else
        echo "✗ Failed to download $file"
        exit 1
    fi
done

echo "All model files downloaded successfully to the 'models' directory!"