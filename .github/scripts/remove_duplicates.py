import sys
import re

def tokenize(line):
    """Split a line on whitespace, keeping "quoted entries with spaces" as a single token"""
    return re.findall(r'"[^"]*"|\S+', line)

def strip_quotes(s):
    """Strip surrounding quotes from a token, if present"""
    if len(s) >= 2 and s.startswith('"') and s.endswith('"'):
        return s[1:-1]
    return s

# An entry from a mod (modname:block, modname:block:meta, modname:block[nbt]) but not a vanilla one
# (minecraft:block, block:property=value, and for old versions block:meta)
MODDED_ENTRY = re.compile(r'^(?!minecraft:)[^\s:=\[\]"]+:(?!\d+(?:,\d+)*(?:[:\[]|$))[^\s:=\[\]]+(?=[:\[]|$)')

def dedupe_parts(parts, seen_entries):
    """Drop repeated mod entries and tag references, the first one stays"""
    kept = []
    for part in parts:
        if part == '\\':
            continue

        if (':' in part or part.startswith('tags_')) and not part.startswith('#'):
            # Use the full part (including blockstate) as the key to check for duplicates
            unique_key = part.rstrip('\\').strip()

            if unique_key not in seen_entries:
                seen_entries.add(unique_key)
                kept.append(part)
        else:
            kept.append(part)
    return kept

def remove_duplicates_in_section(section_lines):
    """Remove duplicate mod entries within a section, preserving different blockstates"""
    if not section_lines:
        return section_lines

    header_line = section_lines[0].rstrip()
    seen_entries = set()

    # The first line stays exactly as it is (1:1 with Complementary), unless it starts with an entry from a
    # mod, like block.21000 = ForgeMultipart:block[parts.id=pr_fixture,...] ... - then repeats are removed too
    key, equals, value = header_line.partition('=')
    header_parts = tokenize(value)
    if equals and header_parts and MODDED_ENTRY.match(header_parts[0]):
        kept = dedupe_parts(header_parts, seen_entries)
        if len(kept) < len([p for p in header_parts if p != '\\']):
            has_backslash = header_line.endswith('\\')
            header_line = key + equals + ' ' + ' '.join(kept)
            if has_backslash:
                header_line += ' \\'

    result = [header_line]

    for i, line in enumerate(section_lines[1:], 1):
        line_stripped = line.rstrip()

        if line_stripped.startswith('#') or not line_stripped.strip() or line_stripped.strip() == '\\':
            result.append(line_stripped)
            continue

        # Process mod entries and tag references. Tokenized (rather than
        # skipping the whole line when 'tags_' appears anywhere in it) so a
        # line mixing a tag with real mod entries is deduped correctly instead
        # of being passed through untouched.
        filtered_parts = dedupe_parts(tokenize(line_stripped), seen_entries)

        if filtered_parts:
            has_backslash = line_stripped.rstrip().endswith('\\')
            reconstructed = ' '.join(filtered_parts)
            if has_backslash and not reconstructed.endswith('\\'):
                reconstructed += ' \\'
            result.append(reconstructed)
        elif line_stripped.strip() == '\\':
            result.append(line_stripped)

    return [line + '\n' for line in result]

def process_properties_file(file_path):
    """Process a properties file to remove duplicates within each section"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        return False
    except Exception as e:
        print(f"Error reading file: {e}")
        return False

    result_lines = []
    i = 0
    duplicates_removed = 0

    while i < len(lines):
        line = lines[i]

        section_match = re.match(r'^(item|block|entity)\.\d+\s*=', line)

        if section_match:
            current_section = [line]
            section_start = i
            section_end = i

            # Find the end of this section (an entry on a single line has no more lines)
            for j in range(i + 1, len(lines) if line.rstrip().endswith('\\') else i + 1):
                current_section.append(lines[j])
                stripped = lines[j].strip()
                if not stripped.endswith('\\') and stripped != '\\':
                    section_end = j
                    break
                section_end = j

            original_count = sum(1 for line in current_section for part in line.split() if ':' in part and part != '\\')

            processed_section = remove_duplicates_in_section(current_section)

            new_count = sum(1 for line in processed_section for part in line.split() if ':' in part and part != '\\')

            if original_count > new_count:
                duplicates_removed += (original_count - new_count)
                print(f"Section {section_match.group()}: Removed {original_count - new_count} duplicate(s)")

            result_lines.extend(processed_section)

            i = section_end + 1
        else:
            result_lines.append(line)
            i += 1

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(result_lines)
        if duplicates_removed > 0:
            print(f"Total duplicates removed: {duplicates_removed}")
        return True
    except Exception as e:
        print(f"Error writing file: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python remove_duplicates.py <path_to_properties_file>")
        return

    file_path = sys.argv[1]
    process_properties_file(file_path)

if __name__ == "__main__":
    main()
