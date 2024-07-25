#!/bin/bash

# Define the source directory for Jupyter notebooks and the target directory for markdown files
NOTEBOOK_DIR="ipynb_docs_for_readthedocs"
MARKDOWN_DIR="docs/source"

# Check if the notebook directory exists
if [ ! -d "$NOTEBOOK_DIR" ]; then
  echo "Directory $NOTEBOOK_DIR does not exist. Exiting."
  exit 1
fi

# Convert all Jupyter notebooks in the notebook directory to markdown
echo "Converting Jupyter notebooks to Markdown..."
for notebook in $NOTEBOOK_DIR/*.ipynb; do
  jupyter nbconvert --to markdown "$notebook"
done

# Move all converted markdown files to the markdown directory
echo "Moving Markdown files to $MARKDOWN_DIR..."
for markdown in $NOTEBOOK_DIR/*.md; do
  mv "$markdown" "$MARKDOWN_DIR"
done

# Build the documentation with Sphinx
echo "Building documentation with Sphinx..."
sphinx-build -b html docs/source/ docs/build/html

# Open the documentation
echo "Opening documentation..."
open docs/build/html/index.html

echo "Documentation build process complete."