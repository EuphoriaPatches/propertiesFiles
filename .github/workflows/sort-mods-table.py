import re
import os

def sort_markdown_table(file_path):
    # Read the file content
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Find the table by splitting at "## Mod List"
    parts = content.split("## Mod List")
    if len(parts) < 2:
        print("Table not found in the format expected")
        return False
    
    # Keep the header and everything before the table
    header = parts[0] + "## Mod List\n"
    
    # Split the rest at the first occurrence of "---" after the table
    table_and_rest = parts[1].split("\n---", 1)
    
    # Extract the table lines (everything up to the "---")
    table_text = table_and_rest[0].strip()
    table_lines = table_text.split('\n')
    
    # The first two lines are the header and separator
    header_rows = table_lines[0:2]
    content_rows = table_lines[2:] if len(table_lines) > 2 else []
    
    # Filter out any rows that don't have proper table formatting
    valid_content_rows = []
    for i, row in enumerate(content_rows):
        if row.strip() and row.count('|') >= 3:  # Need at least 3 pipe characters for a valid row
            valid_content_rows.append(row)
        else:
            print(f"Skipping invalid row {i+3}: '{row}'")
    
    # Sort content rows alphabetically by mod name (first column)
    # Extract the actual mod name, removing Markdown formatting and ignoring comments
    def get_sort_key(row):
        # Get the mod name cell (second column)
        cells = row.split('|')
        if len(cells) <= 1:
            return ""
            
        mod_name_cell = cells[1].strip()
        
        # Extract the name from markdown link if present
        mod_name = re.sub(r'\[([^]]+)\].*', r'\1', mod_name_cell)
        
        # Handle special prefix cases like "[Let's Do]"
        if mod_name.startswith('[') and 'Let\'s Do' in mod_name:
            # Remove the prefix for sorting purposes
            mod_name = mod_name.replace('[Let\'s Do]', '').strip()
        
        # Handle "The" prefix
        if mod_name.startswith('The '):
            mod_name = mod_name[4:]
            
        return mod_name.lower()
    
    sorted_rows = sorted(valid_content_rows, key=get_sort_key)
    
    # Reconstruct the table
    sorted_table = '\n'.join(header_rows + sorted_rows)
    
    # Reconstruct the full content
    if len(table_and_rest) > 1:
        full_content = header + sorted_table + "\n---" + table_and_rest[1]
    else:
        full_content = header + sorted_table
    
    # Write back to file directly
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(full_content)
    
    print("Table sorted successfully.")
    return True

if __name__ == "__main__":
    # Get the repository root directory
    repo_root = os.environ.get('GITHUB_WORKSPACE', '.')
    file_path = os.path.join(repo_root, 'addedMods.md')
    sort_markdown_table(file_path)