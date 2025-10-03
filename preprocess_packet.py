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
    """
    Cleans the entire packet text by removing headers, footers, and standardizing formatting,
    while preserving both tossups and bonuses.
    """
    # 1. Remove common header/footer patterns that appear anywhere in the file
    header_footer_patterns = [
        r'(?im)^.*?(?:page|round|packet|scholastic|scop|outreach|program|copyright|tournament).*?$\n',
        r'(?im)^.*?(?:Brad Fischer|authors|written by|edited by).*?$\n',
        r'(?im)^.*?(?:·|•).*?$\n', # Lines with bullets, often author lists
    ]
    for pattern in header_footer_patterns:
        text = regex.sub(pattern, '', text)

    # 2. Standardize question numbering to use parentheses, e.g., "1. " -> "1) "
    text = regex.sub(r'(?m)^(\s*\d+)[\.]', r'\1)', text)

    # 3. Clean up whitespace and line breaks
    text = regex.sub(r'[ \t]+', ' ', text)  # Collapse multiple spaces/tabs into one
    text = regex.sub(r'\n\s*\n+', '\n\n', text)  # Collapse multiple blank lines
    text = text.strip()

    return text

def process_files(input_dir: str = 'packets', output_dir: str = 'packets_clean'):
    """Processes all text files in the input directory and saves them to the output directory."""
    Path(output_dir).mkdir(exist_ok=True)
    
    for file_path in Path(input_dir).glob('*.txt'):
        print(f"Cleaning {file_path.name}...")
        
        try:
            # Read with UTF-8 encoding, which handles most special characters
            text = file_path.read_text(encoding='utf-8-sig', errors='replace')
            clean_text = clean_packet(text)
            
            # Write cleaned output to the separate 'clean' directory
            output_path = Path(output_dir) / file_path.name
            output_path.write_text(clean_text, encoding='utf-8')
            print(f"Successfully cleaned {file_path.name} -> {output_path}")
            
        except Exception as e:
            print(f"Error processing {file_path.name}: {e}")