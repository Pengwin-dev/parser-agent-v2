#!/usr/bin/env python3
"""
PDF Pitch Deck Parser
Extracts text from PDF presentations and generates summaries.
"""

import fitz  # PyMuPDF
import os
import re
from typing import List, Optional


class PDFParser:
    """Parser for extracting text from PDF pitch deck presentations."""
    
    def __init__(self, pdf_path: str):
        """
        Initialize the PDF parser.
        
        Args:
            pdf_path (str): Path to the PDF file
        """
        self.pdf_path = pdf_path
        self.doc = None
        
    def open_pdf(self) -> bool:
        """
        Open and validate the PDF file.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not os.path.exists(self.pdf_path):
                print(f"Error: File {self.pdf_path} not found.")
                return False
                
            self.doc = fitz.open(self.pdf_path)
            print(f"Successfully opened PDF: {self.pdf_path}")
            print(f"Number of pages: {len(self.doc)}")
            return True
            
        except Exception as e:
            print(f"Error opening PDF: {e}")
            return False
    
    def extract_text_from_page(self, page_num: int) -> str:
        """
        Extract text from a specific page.
        
        Args:
            page_num (int): Page number (0-indexed)
            
        Returns:
            str: Extracted text from the page
        """
        if not self.doc:
            return ""
            
        try:
            page = self.doc[page_num]
            text = page.get_text()
            return text.strip()
        except Exception as e:
            print(f"Error extracting text from page {page_num}: {e}")
            return ""
    
    def extract_all_text(self) -> str:
        """
        Extract text from all pages of the PDF.
        
        Returns:
            str: All extracted text combined
        """
        if not self.doc:
            return ""
            
        all_text = []
        
        for page_num in range(len(self.doc)):
            page_text = self.extract_text_from_page(page_num)
            if page_text:
                all_text.append(f"--- Page {page_num + 1} ---\n{page_text}\n")
        
        return "\n".join(all_text)
    
    def clean_text(self, text: str) -> str:
        """
        Clean and format the extracted text.
        
        Args:
            text (str): Raw extracted text
            
        Returns:
            str: Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page separators
        text = re.sub(r'--- Page \d+ ---', '', text)
        
        # Clean up bullet points and formatting
        text = re.sub(r'•\s*', '- ', text)
        text = re.sub(r'[●◆■□]\s*', '- ', text)
        
        # Remove excessive newlines
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        return text.strip()
    
    def generate_summary(self, text: str) -> str:
        """
        Generate a structured business summary with specific information.
        
        Args:
            text (str): Cleaned text content
            
        Returns:
            str: Generated structured summary
        """
        # Initialize summary sections
        company_name = "Not specified"
        description = "Not specified"
        problem = "Not specified"
        solution = "Not specified"
        funding_info = "Not specified"
        industry_sectors = "Not specified"
        
        # Extract company name (look for patterns like "Company:", "Company Name:", etc.)
        company_patterns = [
            r'Company:\s*([^\n]+)',
            r'Company Name:\s*([^\n]+)',
            r'([A-Z][a-z]+(?:[A-Z][a-z]+)*)\s*Company',
            r'Company:\s*([A-Z][a-z]+(?:[A-Z][a-z]+)*)'
        ]
        
        for pattern in company_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                company_name = match.group(1).strip()
                break
        
        # If no company found, look for the first capitalized word that might be the company name
        if company_name == "Not specified":
            # Look for patterns like "TokenEstate Company:" or "Company: TokenEstate"
            company_match = re.search(r'([A-Z][a-z]+(?:[A-Z][a-z]+)*)', text)
            if company_match:
                company_name = company_match.group(1)
        
        # Extract description (look for sections like "About", "Description", "Overview")
        desc_patterns = [
            r'(?:About|Description|Overview|What we do):\s*([^\n]+(?:\n[^\n]+)*)',
            r'We\s+are\s+([^.]*\.)',
            r'Our\s+mission\s+is\s+([^.]*\.)'
        ]
        
        for pattern in desc_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                description = match.group(1).strip()
                break
        
        # Extract problem statement
        problem_patterns = [
            r'Problem:\s*([^.]*\.)',
            r'Challenge:\s*([^.]*\.)',
            r'The\s+traditional\s+([^.]*\.)',
            r'Current\s+market\s+([^.]*\.)'
        ]
        
        for pattern in problem_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                problem = match.group(1).strip()
                break
        
        # If no explicit problem section, look for problem description in the text
        if problem == "Not specified":
            problem_match = re.search(r'The\s+traditional\s+real\s+estate\s+market\s+is\s+([^.]*\.)', text, re.IGNORECASE)
            if problem_match:
                problem = f"The traditional real estate market is {problem_match.group(1).strip()}"
        
        # Clean up problem text to get just the first sentence
        if problem != "Not specified":
            problem_sentences = problem.split('.')
            if len(problem_sentences) > 0:
                problem = problem_sentences[0].strip() + "."
        
        # Extract solution
        solution_patterns = [
            r'Solution:\s*([^.]*\.)',
            r'How\s+it\s+Works:\s*([^.]*\.)',
            r'Our\s+solution\s+is\s+([^.]*\.)',
            r'We\s+enable\s+([^.]*\.)'
        ]
        
        for pattern in solution_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                solution = match.group(1).strip()
                break
        
        # If no explicit solution section, look for solution description in the text
        if solution == "Not specified":
            solution_match = re.search(r'TokenEstate\s+is\s+a\s+([^.]*\.)', text, re.IGNORECASE)
            if solution_match:
                solution = f"TokenEstate is a {solution_match.group(1).strip()}"
        
        # Clean up solution text to get just the first sentence
        if solution != "Not specified":
            solution_sentences = solution.split('.')
            if len(solution_sentences) > 0:
                solution = solution_sentences[0].strip() + "."
        
        # Extract funding information
        funding_patterns = [
            r'Funding\s+Request:\s*([^\n]+)',
            r'Seed\s+Round:\s*([^\n]+)',
            r'Series\s+[A-Z]:\s*([^\n]+)',
            r'\$([0-9]+(?:\.[0-9]+)?)\s*(?:Million|M|Billion|B)',
            r'Funding:\s*([^\n]+)'
        ]
        
        for pattern in funding_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                funding_info = match.group(1).strip()
                break
        
        # Clean up funding info to get just the key details
        if funding_info != "Not specified":
            # Extract just the funding amount and round type
            funding_clean = re.search(r'(\$[0-9]+(?:\.[0-9]+)?\s*(?:Million|M|Billion|B)?\s*(?:Seed|Series\s+[A-Z])?\s*Round?)', funding_info, re.IGNORECASE)
            if funding_clean:
                funding_info = funding_clean.group(1).strip()
            else:
                # If no clean match, try to extract just the first part
                funding_parts = funding_info.split('-')
                if len(funding_parts) > 0:
                    funding_info = funding_parts[0].strip()
        
        # Extract industry sectors
        industry_patterns = [
            r'Industry:\s*([^\n]+)',
            r'Sector:\s*([^\n]+)',
            r'Market:\s*([^\n]+)',
            r'real\s+estate',
            r'blockchain',
            r'fintech',
            r'technology'
        ]
        
        industries = []
        for pattern in industry_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            industries.extend(matches)
        
        if industries:
            # Clean up and deduplicate industries
            clean_industries = []
            for industry in industries:
                if industry.lower() in ['real estate', 'blockchain', 'fintech', 'technology']:
                    clean_industries.append(industry.lower().title())
                elif len(industry) < 50:  # Only add if it's not too long
                    clean_industries.append(industry.strip())
            
            if clean_industries:
                industry_sectors = ", ".join(set(clean_industries))  # Remove duplicates
        
        # Build structured summary
        summary = "PITCH DECK BUSINESS SUMMARY\n"
        summary += "=" * 50 + "\n\n"
        
        summary += f"Company Name: {company_name}\n\n"
        summary += f"Description: {description}\n\n"
        summary += f"Problem: {problem}\n\n"
        summary += f"Solution: {solution}\n\n"
        summary += f"Funding Info: {funding_info}\n\n"
        summary += f"Industry Sectors: {industry_sectors}\n\n"
        
        # Add metadata
        summary += f"Total pages processed: {len(self.doc) if self.doc else 0}\n"
        summary += f"Total text extracted: {len(text)} characters\n"
        
        return summary
    
    def save_summary(self, summary: str, output_path: Optional[str] = None) -> str:
        """
        Save the summary to a text file.
        
        Args:
            summary (str): Summary text to save
            output_path (str, optional): Output file path. If None, auto-generates.
            
        Returns:
            str: Path to the saved file
        """
        if output_path is None:
            base_name = os.path.splitext(os.path.basename(self.pdf_path))[0]
            output_path = f"{base_name}_summary.txt"
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(summary)
            
            print(f"Summary saved to: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error saving summary: {e}")
            return ""
    
    def close(self):
        """Close the PDF document."""
        if self.doc:
            self.doc.close()
            self.doc = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def main():
    """Main function to run the PDF parser."""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python pdf_parser.py <path_to_pdf>")
        print("Example: python pdf_parser.py presentation.pdf")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    # Create parser and process PDF
    with PDFParser(pdf_path) as parser:
        if not parser.open_pdf():
            sys.exit(1)
        
        print("Extracting text from PDF...")
        raw_text = parser.extract_all_text()
        
        if not raw_text:
            print("No text could be extracted from the PDF.")
            sys.exit(1)
        
        print("Cleaning extracted text...")
        cleaned_text = parser.clean_text(raw_text)
        
        print("Generating summary...")
        summary = parser.generate_summary(cleaned_text)
        
        print("Saving summary...")
        output_file = parser.save_summary(summary)
        
        if output_file:
            print(f"\n✅ Success! Summary saved to: {output_file}")
        else:
            print("\n❌ Failed to save summary.")
            sys.exit(1)


if __name__ == "__main__":
    main()
