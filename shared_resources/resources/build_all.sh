#!/bin/bash

set -e  # Exit on any error

# Validate environment
if ! command -v poetry &> /dev/null; then
    echo "Error: Poetry not found."
    exit 1
fi

echo "Using Poetry: $(which poetry)"
poetry --version

# Create dist directory for all wheels
mkdir -p dist

# Build each subpackage
for package in lift_resources_lists; do
    echo "Building $package..."
    cd "$package"
    
    # Ensure Poetry environment exists for this package
    poetry install --no-root
    
    # Build
    poetry build --format wheel
    
    cp dist/*.whl ../dist/
    cd ..
done

echo "All wheels built successfully in dist/"
ls -lh dist/