#!/usr/bin/env python3
"""
Test script to verify PDF Parser installation
Run this to check if all dependencies are properly installed.
"""

def test_imports():
    """Test if all required modules can be imported."""
    print("Testing imports...")
    
    try:
        import fitz
        print("✅ PyMuPDF (fitz) imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import PyMuPDF: {e}")
        return False
    
    try:
        import nltk
        print("✅ nltk imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import nltk: {e}")
        return False
    
    try:
        from pdf_parser import PDFParser
        print("✅ PDFParser class imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import PDFParser: {e}")
        return False
    
    return True


def test_pdf_parser_class():
    """Test if the PDFParser class can be instantiated."""
    print("\nTesting PDFParser class...")
    
    try:
        from pdf_parser import PDFParser
        
        # Test instantiation
        parser = PDFParser("test.pdf")
        print("✅ PDFParser can be instantiated")
        
        # Test if it's a context manager
        if hasattr(parser, '__enter__') and hasattr(parser, '__exit__'):
            print("✅ PDFParser implements context manager protocol")
        else:
            print("❌ PDFParser does not implement context manager protocol")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing PDFParser class: {e}")
        return False


def main():
    """Main test function."""
    print("PDF Parser Installation Test")
    print("=" * 40)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed. Please check your installation.")
        return False
    
    # Test PDFParser class
    if not test_pdf_parser_class():
        print("\n❌ PDFParser class tests failed.")
        return False
    
    print("\n✅ All tests passed! Your PDF Parser is ready to use.")
    print("\nNext steps:")
    print("1. Place a PDF file in this directory")
    print("2. Run: python pdf_parser.py your_file.pdf")
    print("3. Or use the example: python example_usage.py")
    
    return True


if __name__ == "__main__":
    main()

