# Converts a docx file to a txt file while annotating the bold, italic, and underlined parts (and no other styling).

import docx.text.paragraph
import sys
from pathlib import Path

def parse_paragraph(paragraph: docx.text.paragraph.Paragraph) -> str:
    """Parse a paragraph and maintain formatting annotations.
    
    Args:
        paragraph: A docx paragraph object
    Returns:
        str: Formatted text with annotations
    """
    text = ""
    for runs in paragraph.runs:
        if len(runs.text.strip()) == 0:
            text += runs.text
            continue

        run = runs.text

        if runs.underline:
            run = "{u}" + run + "{/u}"
        if runs.bold:
            run = "{b}" + run + "{/b}"
        if runs.italic:
            run = "{i}" + run + "{/i}"

        text += run

    return text

def convert(docx_path):
    """Convert DOCX to formatted text.
    
    Args:
        docx_path (str): Path to the DOCX file
    Returns:
        str: Formatted text content
    """
    document = docx.Document(docx_path)
    content = []

    for item in document.iter_inner_content():
        if isinstance(item, docx.text.paragraph.Paragraph):
            content.append(parse_paragraph(item))
        else:
            for row in item.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        content.append(parse_paragraph(paragraph))
    
    return '\n'.join(content)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python docx_to_txt.py <docx_file>")
        sys.exit(1)
    print(convert(sys.argv[1]))
