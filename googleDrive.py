import subprocess
import sys
import gdown
from pathlib import Path
from to_text import convertFile

def setup_directories():
    """Create necessary directories if they don't exist."""
    for directory in ['p-pdf', 'packets', 'output']:
        Path(directory).mkdir(exist_ok=True)

def download_file(url: str) -> bool:
    """Download file from Google Drive."""
    pdf_path = "p-docx/packet.docx"
    return gdown.download(url, pdf_path, quiet=False, fuzzy=True)

def run_parser(encoding='utf-8-sig') -> bool:
    """Run packet parser on converted files."""
    command = [
        sys.executable, 
        'packet_parser.py',
        '-p',  # auto-insert powermarks 
        '-f',  # force overwrite
        '-s',  # space powermarks
    ]
    
    try:
        # Run parser with correct encoding
        process = subprocess.run(
            command,
            text=True,
            input='y\nn\n',  # Answers for interactive prompts
            capture_output=True,
            encoding=encoding,
            errors='replace'
        )
        
        # Print output for debugging
        if process.stdout:
            print(process.stdout)
        if process.stderr:
            print("Errors:", process.stderr)
            
        return process.returncode == 0
        
    except Exception as e:
        print(f"Error running parser: {e}")
        return False

def main():
    try:
        # Setup
        setup_directories()
        
        # Get file
        url = input("Enter the url of the file to download: ")
        if not download_file(url):
            print("Failed to download file")
            return
            
        # Convert PDF to text
        print("\nConverting file to text...")
        if not convertFile('d'):
            print("Failed to convert file")
            return
        
        from preprocess_packet import process_files

        # Clean packets with new preprocessing
        print("\nCleaning packets...")
        process_files('packets', 'packets')
        
        # Run parser on cleaned packets
        print("\nParsing packet...")
        if run_parser():
            print("\nSuccessfully parsed packet!")
            print("Check the 'output' directory for results")
        else:
            print("\nFailed to parse packet")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()