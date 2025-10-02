import regex
from pathlib import Path
from typing import List

def extract_tossups(text: str) -> List[str]:
    """Extract individual tossups from text, ignoring headers and footers."""
    
    # Find the tossups section
    tossup_section = regex.search(
        r'{b}Tossups{/b}.*?(?={b}Bonuses{/b}|$)', 
        text, 
        flags=regex.DOTALL | regex.IGNORECASE
    )
    
    if not tossup_section:
        return []

    text = tossup_section.group(0)
    
    # Split into individual tossups using question numbers
    tossups = []
    current_tossup = []
    
    for line in text.split('\n'):
        # Skip empty lines and any header-like content
        if not line.strip() or any(x in line.lower() for x in [
            'round', 'page', 'packet', 'scholastic', 'scop', 
            'outreach', 'program', '·', '•'
        ]):
            continue
            
        # New tossup starts with number)
        if regex.match(r'^\s*\d+\)', line):
            if current_tossup:
                tossups.append(' '.join(current_tossup))
                current_tossup = []
            current_tossup.append(line)
        # Continue current tossup
        elif current_tossup:
            current_tossup.append(line)
    
    # Add final tossup
    if current_tossup:
        tossups.append(' '.join(current_tossup))
    
    return tossups

def clean_packet(text: str) -> str:
    """Clean and standardize packet formatting."""
    
    # Extract just the tossups
    tossups = extract_tossups(text)
    
    if not tossups:
        return text
    
    # Rebuild text with clean tossups only
    clean_text = "{b}Tossups{/b}\n" + "\n\n".join(tossups)
    
    # Clean up formatting
    clean_text = regex.sub(r'\s+', ' ', clean_text)  # Collapse whitespace
    clean_text = regex.sub(r'\s*\n\s*', '\n', clean_text)  # Clean line endings
    clean_text = regex.sub(r'\n{3,}', '\n\n', clean_text)  # Max double newlines
    
    return clean_text.strip()

def process_files(input_dir: str = 'packets', output_dir: str = 'packets_clean'):
    """Process all packet files."""
    Path(output_dir).mkdir(exist_ok=True)
    
    for file_path in Path(input_dir).glob('*.txt'):
        print(f"Cleaning {file_path.name}...")
        
        try:
            # Read with UTF-8 encoding
            text = file_path.read_text(encoding='utf-8-sig')
            clean_text = clean_packet(text)
            
            # Write cleaned output
            output_path = Path(output_dir) / file_path.name
            output_path.write_text(clean_text, encoding='utf-8-sig')
            print(f"Successfully cleaned {file_path.name}")
            
        except Exception as e:
            print(f"Error processing {file_path.name}: {e}")