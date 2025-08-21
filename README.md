# PDF Pitch Deck Parser

A Python-based PDF parser that extracts text from pitch deck presentations and generates clean summaries in text format.

## Features

- **Text Extraction**: Extracts text from all pages of PDF documents
- **Smart Cleaning**: Removes formatting artifacts and excessive whitespace
- **Summary Generation**: Creates concise summaries focusing on meaningful content
- **Clean Output**: Saves summaries as well-formatted .txt files
- **Error Handling**: Robust error handling for various PDF formats
- **Context Manager**: Safe resource management with automatic cleanup

## Installation

1. **Clone or download** this repository to your local machine

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Command Line Interface

The simplest way to use the parser:

```bash
python pdf_parser.py your_presentation.pdf
```

This will:
- Extract text from all pages
- Clean and format the content
- Generate a summary
- Save it as `your_presentation_summary.txt`

### Programmatic Usage

You can also use the parser in your own Python code:

```python
from pdf_parser import PDFParser

# Process a PDF file
with PDFParser("presentation.pdf") as parser:
    if parser.open_pdf():
        # Extract all text
        raw_text = parser.extract_all_text()
        
        # Clean the text
        cleaned_text = parser.clean_text(raw_text)
        
        # Generate summary
        summary = parser.generate_summary(cleaned_text)
        
        # Save to custom filename
        parser.save_summary(summary, "my_summary.txt")
```

### Example Script

Run the included example:

```bash
python example_usage.py
```

**Note**: Edit `example_usage.py` and replace `"your_presentation.pdf"` with your actual PDF file path.

## How It Works

1. **PDF Opening**: Uses PyMuPDF to open and validate PDF files
2. **Text Extraction**: Extracts text from each page while preserving structure
3. **Text Cleaning**: 
   - Removes excessive whitespace
   - Cleans up bullet points and formatting
   - Removes page separators
4. **Summary Generation**: 
   - Identifies meaningful paragraphs
   - Creates a structured summary
   - Includes metadata (page count, character count)
5. **Output**: Saves clean summary to a .txt file

## Output Format

The generated summary includes:

```
PITCH DECK SUMMARY
==================================================

1. [First meaningful paragraph content]

2. [Second meaningful paragraph content]

3. [Third meaningful paragraph content]

4. [Fourth meaningful paragraph content]

5. [Fifth meaningful paragraph content]

Total pages processed: [number]
Total text extracted: [character count]
```

## Requirements

- Python 3.6+
- PyMuPDF (fitz)
- nltk (for text processing)

## Supported PDF Types

- Standard PDF documents
- PDF presentations
- Pitch decks with mixed content (text + images)
- Multi-page documents

## Error Handling

The parser handles common issues:
- Missing or corrupted PDF files
- Password-protected PDFs (basic support)
- PDFs with no extractable text
- File permission issues

## Customization

You can customize the parser by modifying:

- **Summary length**: Change the number of paragraphs in `generate_summary()`
- **Text cleaning**: Modify the `clean_text()` method for different formatting needs
- **Output format**: Customize the summary structure in `generate_summary()`

## Troubleshooting

### Common Issues

1. **"No text could be extracted"**
   - The PDF might be image-based or scanned
   - Try a different PDF file

2. **"Error opening PDF"**
   - Check if the file exists and is accessible
   - Ensure the file is a valid PDF

3. **Import errors**
   - Make sure you've installed requirements: `pip install -r requirements.txt`

### Getting Help

If you encounter issues:
1. Check that your PDF file is valid and accessible
2. Ensure all dependencies are installed
3. Try with a simple, text-based PDF first

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the parser.

