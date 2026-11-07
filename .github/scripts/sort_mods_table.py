#!/usr/bin/env python3
"""
Sorts the mod table in addedMods.md alphabetically by mod name and removes trailing whitespace.

Usage: sort_mods_table.py [file path]      (defaults to addedMods.md)
"""
import re
import sys


def get_sort_key(row):
    cells = row.split('|')
    if len(cells) <= 1:
        return ""

    mod_name_cell = cells[1].strip()

    # Extract the name from markdown link if present
    mod_name = re.sub(r'\[([^]]+)\].*', r'\1', mod_name_cell)

    # Handle special prefix cases like "[Let's Do]"
    if mod_name.startswith('[') and 'Let\'s Do' in mod_name:
        mod_name = mod_name.replace('[Let\'s Do]', '').strip()

    # Handle "The" prefix
    if mod_name.startswith('The '):
        mod_name = mod_name[4:]

    return mod_name.lower()


def sort_markdown_table(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    lines = content.split('\n')
    lines = [line.rstrip() for line in lines]
    content = '\n'.join(lines)

    parts = content.split("## Mod List")
    if len(parts) < 2:
        print("ERROR: Table not found in the format expected")
        return False

    header = parts[0] + "## Mod List\n"

    table_and_rest = parts[1].split("\n---", 1)

    table_text = table_and_rest[0].strip()
    table_lines = table_text.split('\n')

    # The first two lines are the header and separator
    header_rows = table_lines[0:2]
    content_rows = table_lines[2:] if len(table_lines) > 2 else []

    original_count = len(content_rows)

    valid_content_rows = []
    for i, row in enumerate(content_rows):
        if row.strip() and row.count('|') >= 3:  # Need at least 3 pipe characters for a valid row
            valid_content_rows.append(row)
        else:
            print(f"WARNING: Skipping invalid row {i+3}: '{row}'")

    valid_count = len(valid_content_rows)

    sorted_rows = sorted(valid_content_rows, key=get_sort_key)

    sorted_table = '\n'.join(header_rows + sorted_rows)

    if len(table_and_rest) > 1:
        full_content = header + sorted_table + "\n---" + table_and_rest[1]
    else:
        full_content = header + sorted_table

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(full_content)

    print(f"SUCCESS: Table sorted and trailing whitespaces removed. Processed {valid_count}/{original_count} rows.")
    return True


if __name__ == "__main__":
    file_path = sys.argv[1] if len(sys.argv) > 1 else "addedMods.md"
    print(f"Processing file: {file_path}")
    if sort_markdown_table(file_path):
        print("Sort operation and whitespace removal completed successfully")
    else:
        print("Operation failed")
        sys.exit(1)
