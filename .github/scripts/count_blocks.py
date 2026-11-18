import os
import re

def tokenize(line):
    """Split a line on whitespace, keeping "quoted entries with spaces" as a single token"""
    return re.findall(r'"[^"]*"|\S+', line)

def strip_quotes(s):
    """Strip surrounding quotes from a token, if present"""
    if len(s) >= 2 and s.startswith('"') and s.endswith('"'):
        return s[1:-1]
    return s

def update_readme_with_block_count(count):
    """Update README.md with the current block count"""
    import re
    readme_path = "README.md"

    if not os.path.exists(readme_path):
        print(f"Warning: {readme_path} not found")
        return False

    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if count >= 1000000:
            formatted_count = f"{count/1000000:.2f}M"
        elif count >= 1000:
            formatted_count = f"{count/1000:.2f}K"
        else:
            formatted_count = str(count)

        print(f"Formatted count: {formatted_count}")

        start_marker = "## Current Total Modded Blocks: <ins>"
        end_marker = "</ins>"

        start_index = content.find(start_marker)
        if start_index != -1:
            start_index += len(start_marker)
            end_index = content.find(end_marker, start_index)
            if end_index != -1:
                updated_content = content[:start_index] + formatted_count + content[end_index:]

                # Now update the exact count line below (format: [54382]: #)
                exact_count_pattern = r'\[\d+\]: #'
                match = re.search(exact_count_pattern, updated_content[end_index:])
                if match:
                    match_start = end_index + match.start()
                    match_end = end_index + match.end()
                    updated_content = updated_content[:match_start] + f"[{count}]: #" + updated_content[match_end:]
                    print(f"Updated exact count reference: [{count}]: #")
                else:
                    print("Warning: Exact count reference line not found")

                with open(readme_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)

                print(f"README.md updated with block count: {formatted_count}")
                return True

        print(f"Warning: Count section not found in README.md")
        return False

    except Exception as e:
        print(f"Error updating README.md: {str(e)}")
        return False

def main():
    block_properties_folder = "blockProperties"
    print(f"Counting unique modded blocks in {block_properties_folder}...")

    total_count = 0
    unique_blocks = set()

    for root, dirs, files in os.walk(block_properties_folder):
        for file in files:
            if file.endswith('.properties'):
                file_path = os.path.join(root, file)
                print(f"Processing: {file_path}")

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()

                    for line in lines:
                        line = line.strip()

                        if not line or line.startswith('#'):
                            continue

                        if line.startswith('block.'):
                            equal_sign_index = line.find('=')
                            if equal_sign_index > 0:
                                line = line[equal_sign_index + 1:].strip()

                        if line == '\\':
                            continue

                        potential_ids = tokenize(line)

                        for block_id in potential_ids:
                            if not block_id or block_id == '\\' or block_id.startswith('%') or block_id.startswith('tags_'):
                                continue

                            if ':' in block_id:
                                parts = strip_quotes(block_id).split(':')

                                # If it has at least 2 parts and the first part isn't a blockstate
                                if len(parts) >= 2 and '=' not in parts[0]:
                                    mod_block_id = f"{parts[0]}:{parts[1]}"
                                    unique_blocks.add(mod_block_id)

                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}")

    total_count = len(unique_blocks)
    print(f"Found {total_count} unique modded blocks across all files")

    update_readme_with_block_count(total_count)

if __name__ == "__main__":
    main()
