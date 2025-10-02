import os
import sys
from pathlib import Path
from modules import pdf_to_docx
from modules import docx_to_txt

def get_file_type(type='p'):
    file_type = os.getenv('TYPE')
    if not file_type:
        while True:
            file_type = type #input("File type (p = pdf, d = docx, c = doc, t = txt): ").lower()
            if file_type in ['p', 'pdf']:
                return 'pdf'
            elif file_type in ['d', 'docx']:
                return 'docx'
            elif file_type in ['c', 'doc']:
                return 'doc'
            elif file_type in ['t', 'txt']:
                return 'txt'
            print("Invalid file type")
    return file_type

def convertFile(type='p'):
    file_type = get_file_type(type)
    print(f"Parsing {file_type} to text...")
    
    # Create packets directory if it doesn't exist
    Path("packets").mkdir(exist_ok=True)
    
    # Process files
    counter = 0
    source_dir = Path(f"p-{file_type}")
    
    for file_path in source_dir.glob(f"*.{file_type}"):
        print(f"Parsing {file_path}...")
        counter += 1
        basename = file_path.name
        
        if file_type == "pdf":
            docx_path = file_path.with_suffix('.docx')
            pdf_to_docx.convert(str(file_path))
            text_content = docx_to_txt.convert(str(docx_path))
            
            output_path = Path("packets") / basename.replace('.pdf', '.txt')
            # Remove U+202D characters and handle other unrecognized chars
            text_content = text_content.encode('utf-8', errors='replace').decode('utf-8')
            text_content = text_content.replace('\u202D', '').replace('\u202C', '').replace('�', ' ')
            output_path.write_text(text_content, encoding='utf-8')
            
        elif file_type == "docx":
            text_content = docx_to_txt.convert(str(file_path))
            output_path = Path("packets") / basename.replace('.docx', '.txt')
            # Write with UTF-8 encoding
            output_path.write_text(text_content, encoding='utf-8', errors='replace')
            
        elif file_type == "txt":
            output_path = Path("packets") / basename
            file_path.rename(output_path)
    
    print(f"Parsed {counter} {file_type}s.")
    return True