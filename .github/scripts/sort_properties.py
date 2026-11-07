import os
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

def natural_key(s):
    """Sort key that orders numbers by value: kryp_blockz_2 comes before kryp_blockz_10"""
    return [int(part) if i % 2 else part for i, part in enumerate(re.split(r'(\d+)', s))]

def entry_key(token):
    return natural_key(strip_quotes(token))

DIMENSION_RE = re.compile(r'^(dimension\.[^\s=]+\s*=\s*)')
PREPROCESSOR_RE = re.compile(r'^#(if|ifdef|ifndef|elif|else|endif|define|undef)\b')

def collect_dimension_section(lines, start):
    section = [lines[start]]
    j = start + 1
    while section[-1].rstrip().endswith('\\') and j < len(lines):
        if PREPROCESSOR_RE.match(lines[j].strip()):
            break
        section.append(lines[j])
        j += 1
    return section, j

# Dimensions with no : part never move
def process_dimension_section(section_lines):
    prefix = DIMENSION_RE.match(section_lines[0]).group(1)

    body = list(section_lines)
    trailing_blank = 0
    while len(body) > 1 and not body[-1].strip():
        body.pop()
        trailing_blank += 1

    group_index = 0
    header_plain = []
    trailing_plain = []
    header_has_mod = False
    mods = {}
    seen = set()
    comments = []  # (appears_after_first_mod, text)
    first_mod_seen = False

    for idx, raw in enumerate(body):
        text = raw[len(prefix):] if idx == 0 else raw
        stripped = text.strip()

        if idx > 0 and stripped.startswith('#'):
            comments.append((first_mod_seen, raw.rstrip()))
            continue

        # A standalone backslash line is the separator between groups
        if idx > 0 and stripped == '\\':
            group_index += 1
            continue

        for token in tokenize(stripped):
            token = token.rstrip('\\')
            if not token or token in seen:
                continue
            seen.add(token)

            if ':' in strip_quotes(token):
                first_mod_seen = True
                if idx == 0:
                    header_has_mod = True
                mod_name = strip_quotes(token).split(':')[0]
                mods.setdefault(mod_name, []).append(token)
            elif group_index == 0:
                header_plain.append(token)
            else:
                trailing_plain.append(token)

    # Nothing to sort (e.g. dimension.world0=* or an empty dimension.world_space=)
    if not mods:
        return section_lines

    group_lines = [' '.join(sorted(mods[name], key=entry_key)) for name in sorted(mods)]
    header_gets_group = header_has_mod or not header_plain
    header_text = ' '.join(header_plain + (group_lines[:1] if header_gets_group else []))
    rest = group_lines[1:] if header_gets_group else group_lines

    units = [prefix + header_text] + rest
    if trailing_plain:
        units.append(' '.join(trailing_plain))

    comments_before = [text for after, text in comments if not after]
    comments_after = [text for after, text in comments if after]

    result = []
    for i, unit in enumerate(units):
        if i == len(units) - 1:
            result.append(f"{unit}\n")
        else:
            result.append(f"{unit} \\\n")
            if i == 0:
                result.extend(f"{c}\n" for c in comments_before)
            result.append("\\\n")
    if len(units) == 1:
        result.extend(f"{c}\n" for c in comments_before)
    result.extend(f"{c}\n" for c in comments_after)
    result.extend("\n" for _ in range(trailing_blank))

    return result

def sort_properties_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        original_lines = f.readlines()

    result_lines = []
    i = 0

    while i < len(original_lines):
        line = original_lines[i]

        # dimension.<name> = sections are handled by their own sorter
        if DIMENSION_RE.match(line):
            dimension_section, i = collect_dimension_section(original_lines, i)
            result_lines.extend(process_dimension_section(dimension_section))
            continue

        section_match = re.match(r'^(item|block|entity)\.\d+\s*=', line)

        if section_match:
            current_section = [line]
            section_end = i

            for j in range(i + 1, len(original_lines)):
                section_end = j
                if not original_lines[j].strip().endswith('\\'):
                    current_section.append(original_lines[j])
                    break
                current_section.append(original_lines[j])

            processed_section = process_section(current_section)
            result_lines.extend(processed_section)

            i = section_end + 1
        else:
            result_lines.append(line)
            i += 1

    return result_lines

def process_section(section_lines):
    """Process a section to sort mod entries alphabetically both vertically and
    horizontally. Any tags_ reference found anywhere in the section - even mixed
    into the same line as real mod entries - is pulled out and placed on its own
    line directly after the header, so it can never be silently dropped."""
    # Special case: Check if the section only has a header that contains a mod
    if len(section_lines) <= 2 and ':' in section_lines[0]:
        return section_lines

    has_content = False
    for line in section_lines[1:]:  # Skip header
        stripped = line.strip()
        if not stripped.startswith('#') and (':' in stripped or 'tags_' in stripped):
            has_content = True
            break

    if not has_content:
        return section_lines

    header_line = section_lines[0].rstrip()

    header_has_mod = ':' in header_line and not header_line.startswith('#')
    header_mod_entries = []
    tag_entries = []
    seen_tags = set()

    if header_has_mod:
        parts = header_line.split('=')
        section_id = parts[0].strip()
        mod_parts = tokenize(parts[1].strip().rstrip('\\').strip())

        for part in mod_parts:
            if part.startswith('tags_'):
                if part not in seen_tags:
                    seen_tags.add(part)
                    tag_entries.append(part)
            elif ':' in part:
                header_mod_entries.append(part)

    mod_entries = {}

    for entry in header_mod_entries:
        mod_name = strip_quotes(entry).split(':')[0]
        if mod_name not in mod_entries:
            mod_entries[mod_name] = []
        mod_entries[mod_name].append(entry)

    # Track where the first real mod entry shows up so comments can still be
    # bucketed into "before" vs "after" the entry block once tags are pulled out
    first_entry_index = None
    comment_lines = []

    for i, line in enumerate(section_lines):
        line = line.strip()

        if not line or line == '\\':
            continue

        if line.startswith('#'):
            comment_lines.append((i, section_lines[i].rstrip()))
            continue

        if i == 0:
            continue

        # Tokenize every content line so a tags_ reference is found and moved
        # regardless of whether it's alone on a line or mixed with mod entries
        has_real_entry = False
        for part in tokenize(line):
            if part == '\\':
                continue

            if part.startswith('tags_'):
                tag = part.rstrip('\\').strip()
                if tag not in seen_tags:
                    seen_tags.add(tag)
                    tag_entries.append(tag)
            elif ':' in part and not part.startswith('#'):
                has_real_entry = True
                mod_name = strip_quotes(part).split(':')[0]

                if mod_name not in mod_entries:
                    mod_entries[mod_name] = []

                entry = part.rstrip('\\').strip()
                mod_entries[mod_name].append(entry)

        if has_real_entry and first_entry_index is None:
            first_entry_index = i

    if first_entry_index is None:
        first_entry_index = len(section_lines)

    sorted_mod_names = sorted(mod_entries.keys())
    sorted_tags = sorted(tag_entries, key=natural_key)

    effective_mod_count = 0
    for mod_name in sorted_mod_names:
        if not (header_has_mod and all(entry in header_mod_entries for entry in mod_entries[mod_name])):
            effective_mod_count += 1

    result = []

    has_body = bool(sorted_mod_names) or bool(sorted_tags)

    if has_body and not header_line.endswith('\\'):
        result.append(f"{header_line} \\\n")
    else:
        result.append(f"{header_line}\n")

    # Add a single combined tag line right after the header, so a tag can
    # never again be silently dropped by being mixed into an entry line
    if sorted_tags:
        tags_line = ' '.join(sorted_tags)
        if effective_mod_count > 0:
            result.append(f"{tags_line} \\\n")
        else:
            result.append(f"{tags_line}\n")

    for i, comment in comment_lines:
        if i < first_entry_index:
            result.append(f"{comment}\n")

    if effective_mod_count > 0:
        result.append("\\\n")

    processed_count = 0
    for i, mod_name in enumerate(sorted_mod_names):
        # Skip mod entries that were in the header if preserving header
        if header_has_mod and all(entry in header_mod_entries for entry in mod_entries[mod_name]):
            continue

        processed_count += 1

        sorted_entries = sorted(mod_entries[mod_name], key=entry_key)

        entries = ' '.join(sorted_entries)

        if processed_count < effective_mod_count:
            result.append(f"{entries} \\\n")
            result.append("\\\n")
        else:
            result.append(f"{entries}\n")

    for i, comment in comment_lines:
        if i >= first_entry_index:
            result.append(f"{comment}\n")

    return result

def main():
    if len(sys.argv) < 2:
        print("Usage: python sort_properties.py <path_to_properties_file>")
        return

    file_path = sys.argv[1]

    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found")
        return

    sorted_lines = sort_properties_file(file_path)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(sorted_lines)

    print(f"File {file_path} sorted successfully!")

if __name__ == "__main__":
    main()
