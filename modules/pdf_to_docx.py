from pdf2docx import Converter
import sys
from pathlib import Path

def convert(pdf_path):
    """Convert PDF to DOCX file.
    
    Args:
        pdf_path (str): Path to the PDF file
    Returns:
        str: Path to the generated DOCX file
    """
    pdf_file = Path(pdf_path)
    docx_file = pdf_file.with_suffix('.docx')
    
    cv = Converter(str(pdf_file))
    cv.convert(str(docx_file))
    cv.close()
    
    return str(docx_file)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pdf_to_docx.py <pdf_file>")
        sys.exit(1)
    convert(sys.argv[1])
