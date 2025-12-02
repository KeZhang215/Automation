#!/usr/bin/env python3
"""
PDF Merger Script
Merges multiple PDF files into a single PDF document.
"""

import sys
from pathlib import Path
from PyPDF2 import PdfMerger


def merge_pdfs(pdf_files, output_file):
    """
    Merge multiple PDF files into a single PDF.

    Args:
        pdf_files: List of PDF file paths to merge
        output_file: Output file path for the merged PDF
    """
    merger = PdfMerger()

    try:
        for pdf_file in pdf_files:
            pdf_path = Path(pdf_file)
            if not pdf_path.exists():
                print(f"Error: File '{pdf_file}' not found.")
                return False

            if not pdf_path.suffix.lower() == '.pdf':
                print(f"Warning: '{pdf_file}' is not a PDF file. Skipping.")
                continue

            print(f"Adding: {pdf_file}")
            merger.append(str(pdf_path))

        print(f"\nMerging PDFs into: {output_file}")
        merger.write(output_file)
        merger.close()
        print("Successfully merged PDFs!")
        return True

    except Exception as e:
        print(f"Error merging PDFs: {e}")
        return False


def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 3:
        print("Usage: python pdf_merger.py <output.pdf> <input1.pdf> <input2.pdf> ...")
        print("\nExample:")
        print("  python pdf_merger.py merged.pdf file1.pdf file2.pdf file3.pdf")
        sys.exit(1)

    output_file = sys.argv[1]
    input_files = sys.argv[2:]

    if not output_file.lower().endswith('.pdf'):
        output_file += '.pdf'

    print(f"Merging {len(input_files)} PDF files...\n")
    success = merge_pdfs(input_files, output_file)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

"""
Example usage:
cd ~/Desktop/folder_name
pthon3 pdf.merger.py output.pdf input1.pdf input2.pdf input3.pdf 
#making sure these files are in the same directory

Usage
python pdf_merger.py <output.pdf> <input1.pdf> <input2.pdf> ...
Example:
python pdf_merger.py merged.pdf file1.pdf file2.pdf file3.pdf
Features
- Merges multiple PDF files in the order specified
- Validates that input files exist
- Checks file extensions
- Provides clear error messages
- Automatically adds .pdf extension to output if missing
The script will combine all the input PDFs into a single output file. 
Just run the installation command above to get started!

"""