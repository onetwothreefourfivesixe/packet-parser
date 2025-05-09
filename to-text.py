import os
import sys
from pathlib import Path
from modules import pdf_to_docx
from modules import docx_to_txt

def get_file_type():
    file_type = os.getenv('TYPE')
    if not file_type:
        while True:
            file_type = input("File type (p = pdf, d = docx, c = doc, t = txt): ").lower()
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

def main():
    file_type = get_file_type()
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
            # Import only when needed
            
            docx_path = file_path.with_suffix('.docx')
            pdf_to_docx.convert(str(file_path))
            text_content = docx_to_txt.convert(str(docx_path))
            
            output_path = Path("packets") / basename.replace('.pdf', '.txt')
            output_path.write_text(text_content)
            
        elif file_type == "docx":
            text_content = docx_to_txt.convert(str(file_path))
            output_path = Path("packets") / basename.replace('.docx', '.txt')
            output_path.write_text(text_content)
            
        elif file_type == "txt":
            output_path = Path("packets") / basename
            file_path.rename(output_path)
    
    print(f"Parsed {counter} {file_type}s.")

if __name__ == "__main__":
    main()