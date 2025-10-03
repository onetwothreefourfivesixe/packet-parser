import subprocess
import sys
import gdown
import os
import time
from pathlib import Path
from to_text import convertFile
from preprocess_packet import process_files
import shutil

def setup_directories():
    """Create all necessary directories for various file types."""
    dirs = ['downloadedPackets', 'p-pdf', 'p-docx', 'p-doc', 'p-txt', 'packets', 'packets_clean', 'output']
    for directory in dirs:
        Path(directory).mkdir(exist_ok=True)
        clear_folder_contents(directory)

def clear_folder_contents(folder_path):
    """
    Deletes all files and subfolders within the specified folder.
    """
    if os.path.exists(folder_path):
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)  # Remove file or symlink
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path) # Remove subfolder and its contents
        # print(f"Contents of '{folder_path}' cleared.")
    else:
        print(f"Folder '{folder_path}' does not exist.")

def download_file(url: str) -> Path | None:
    """
    Downloads a file from Google Drive, waits for it to complete,
    and handles the .part file race condition by polling.
    """
    download_dir = Path('downloadedPackets')
    print(f"Downloading to temporary directory: {download_dir}")

    files_before = set(os.listdir(download_dir))
    
    # Start the download. This call is blocking but the rename might be delayed.
    gdown.download(url, output=str(download_dir) + "/packet.pdf", quiet=False, fuzzy=True)
    
    # Poll the directory to find the final, renamed file.
    timeout_seconds = 10
    start_time = time.time()
    while time.time() - start_time < timeout_seconds:
        files_after = set(os.listdir(download_dir))
        new_files = files_after - files_before
        
        # Filter out the temporary .part file
        final_files = [f for f in new_files if not f.endswith('.part')]
        
        if len(final_files) == 1:
            new_file_name = final_files[0]
            print(f"Download complete. Final file found: {new_file_name}")
            return download_dir / new_file_name
        
        # Wait a moment before checking again
        time.sleep(0.2)

    print(f"Error: Download timed out after {timeout_seconds} seconds. No completed file found.")
    return None

def detect_and_move_file(downloaded_path: Path) -> str | None:
    """Detects the file type from its extension and moves it to the correct p-* directory."""
    suffix = downloaded_path.suffix.lower()
    type_map = {
        '.pdf': 'p',
        '.docx': 'd',
        '.doc': 'c',
        '.txt': 't'
    }

    if suffix not in type_map:
        print(f"Error: Unsupported file type '{suffix}'. Cannot process the file.")
        downloaded_path.unlink()  # Clean up the downloaded file
        return None

    type_code = type_map[suffix]
    # The to_text.py script expects source files in p-* directories
    file_type_name = suffix.replace('.', '') # Turns '.pdf' into 'pdf'
    dest_dir_name = f'p-{file_type_name}'
    dest_dir = Path(dest_dir_name)
    
    # Move the file to the correct processing directory
    dest_path = dest_dir / downloaded_path.name
    downloaded_path.rename(dest_path)
    print(f"Detected file type '{suffix}'. Moved file to '{dest_dir}'.")
    return type_code

def run_parser() -> bool:
    """Run packet parser non-interactively on the cleaned files."""
    command = [
        sys.executable, 
        'packet_parser.py',
        '--input-directory', 'packets_clean',  # Use the cleaned files
        '--output-directory', 'output',
        '--has-category-tags',
        '-p',  # auto-insert powermarks 
        '-f',  # force overwrite
        '-s',  # space powermarks
    ]
    
    try:
        process = subprocess.run(
            command, text=True, capture_output=True, encoding='utf-8', errors='replace'
        )
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
        setup_directories()
        
        url = input("Enter the Google Drive URL of the file to download: ")
        
        downloaded_path = download_file(url)
        if not downloaded_path:
            print("Failed to download file.")
            return

        type_code = detect_and_move_file(downloaded_path)
        if not type_code:
            return # Error message was already printed in the function
            
        print("\nConverting file to text...")
        if not convertFile():
            print("Failed to convert file.")
            return
        
        print("\nCleaning packet text...")
        process_files('packets', 'packets_clean')
        
        print("\nParsing packet...")
        if run_parser():
            print("\nSuccessfully parsed packet! Check the 'output' directory.")
        else:
            print("\nFailed to parse packet.")
            
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()