#!/usr/bin/env python3
"""
Example usage of the PDF Parser
Demonstrates how to use the PDFParser class programmatically.
"""

from pdf_parser import PDFParser


def process_pdf_example(pdf_path: str):
    """
    Example function showing how to use the PDFParser class.
    
    Args:
        pdf_path (str): Path to the PDF file to process
    """
    print(f"Processing PDF: {pdf_path}")
    print("-" * 50)
    
    # Use the parser with context manager for automatic cleanup
    with PDFParser(pdf_path) as parser:
        # Open the PDF
        if not parser.open_pdf():
            print("Failed to open PDF. Exiting.")
            return
        
        # Extract text from all pages
        print("Extracting text...")
        raw_text = parser.extract_all_text()
        
        if not raw_text:
            print("No text extracted. Exiting.")
            return
        
        # Clean the extracted text
        print("Cleaning text...")
        cleaned_text = parser.clean_text(raw_text)
        
        # Generate summary
        print("Generating summary...")
        summary = parser.generate_summary(cleaned_text)
        
        # Save summary with custom filename
        custom_output = "custom_summary.txt"
        output_file = parser.save_summary(summary, custom_output)
        
        if output_file:
            print(f"✅ Summary saved to: {output_file}")
        else:
            print("❌ Failed to save summary")


def main():
    """Main function for the example."""
    # Example PDF path - replace with your actual PDF file
    pdf_file = "your_presentation.pdf"
    
    print("PDF Pitch Deck Parser - Example Usage")
    print("=" * 50)
    
    # Check if the example file exists
    import os
    if not os.path.exists(pdf_file):
        print(f"Example file '{pdf_file}' not found.")
        print("Please replace 'your_presentation.pdf' with the path to your actual PDF file.")
        print("\nOr run the command line version:")
        print("python pdf_parser.py your_presentation.pdf")
        return
    
    # Process the PDF
    process_pdf_example(pdf_file)


if __name__ == "__main__":
    main()
