import os
import re
import json

def split_txt_by_size_with_anchor(src, out_dir, max_mb=10.0, anchor="IN THIS SECTION"):
    os.makedirs(out_dir, exist_ok=True)
    max_bytes = int(max_mb * 1024 * 1024)

    with open(src, "r", encoding="utf-8") as f:
        text = f.read()

    parts = []
    start = 0
    n = len(text)

    while start < n:
        end = min(start + max_bytes, n)
        if end < n:
            anchor_pos = text.rfind("\n" + anchor + "\n", start, end)
            if anchor_pos > start:
                end = anchor_pos
        parts.append(text[start:end])
        start = end

    out_files = []
    for i, part in enumerate(parts, 1):
        out_path = os.path.join(out_dir, f"junos_cli_part_{i:03d}.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(part)
        out_files.append(out_path)
    return out_files

def strip_page_numbers(s):
    return re.sub(r"^\s*\d+\s*$", "", s, flags=re.M).strip()

def clean_toc_noise(text):
    return re.sub(r"^[^\n]+\s+\|\s+\d+\s*$", "", text, flags=re.M)

def is_valid_command(cmd):
    cmd = cmd.strip()
    if not cmd:
        return False
    if len(cmd) == 1 and cmd.isalpha():
        return False
    if re.fullmatch(r"\d+", cmd):
        return False
    return True

def clean_lines(lines):
    return [l for l in (x.strip() for x in lines) if l and not re.fullmatch(r"\d+", l)]

def split_blocks(text):
    blocks = []
    for m in re.finditer(r"\n([^\n]+)\nIN THIS SECTION\n", text):
        cmd = m.group(1).strip()
        if is_valid_command(cmd):
            blocks.append((cmd, m.start()))
    result = []
    for i, (cmd, start) in enumerate(blocks):
        end = blocks[i + 1][1] if i + 1 < len(blocks) else len(text)
        body = text[start:end]
        result.append((cmd, body))
    return result

def parse_sections(body):
    headers = [
        "Syntax",
        "Hierarchy Level",
        "Description",
        "Options",
        "Required Privilege Level",
        "Release Information",
        "RELATED DOCUMENTATION"
    ]
    positions = []
    for h in headers:
        for m in re.finditer(rf"\n{re.escape(h)}(?:\s*\([^)]+\))?\n", body):
            positions.append((m.start(), h))
    positions.sort()
    sections = {h: "" for h in headers}
    for i, (pos, h) in enumerate(positions):
        start = pos
        header_line = re.search(r"\n([^\n]+)\n", body[start:])
        if header_line:
            start = start + header_line.end()
        end = positions[i + 1][0] if i + 1 < len(positions) else len(body)
        sections[h] = strip_page_numbers(body[start:end])
    return sections

def merge_hyphenated(lines):
    merged = []
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if line.endswith("-") and i + 1 < len(lines):
            merged.append(line + lines[i + 1].lstrip())
            i += 2
        else:
            merged.append(line)
            i += 1
    return merged


def is_option_name(line):
    if not line:
        return False
    if line.endswith("."):
        return False
    if line.lower().startswith(("default:", "range:", "note:", "the remaining statements")):
        return False
    if len(line) > 45:
        return False
    if re.match(r"^[A-Z][a-z].+", line):
        return False
    return True

def parse_options(raw):
    if not raw:
        return []
    lines = clean_lines(raw.splitlines())
    lines = [l.lstrip("• ").strip() for l in lines if l.strip()]
    lines = merge_hyphenated(lines)

    options = []
    cur_name = ""
    cur_desc = ""

    def flush():
        nonlocal cur_name, cur_desc
        if cur_name:
            options.append({"name": cur_name.strip(), "desc": cur_desc.strip()})
        cur_name, cur_desc = "", ""

    for line in lines:
        if line == "The remaining statements are explained separately. See CLI Explorer.":
            continue
        if "—" in line:
            flush()
            name, desc = line.split("—", 1)
            options.append({"name": name.strip(), "desc": desc.strip()})
            continue
        if is_option_name(line):
            flush()
            cur_name = line
            continue
        if cur_name:
            cur_desc += (" " if cur_desc else "") + line

    flush()
    return [o for o in options if o["name"]]

def clean_related(raw):
    if not raw:
        return []
    lines = clean_lines(raw.splitlines())
    drop = {"related documentation", "in this section"}
    return [l for l in lines if l.lower() not in drop and l != "A"]

def extract_commands(text):
    text = clean_toc_noise(text)
    blocks = split_blocks(text)
    items = []
    for cmd, body in blocks:
        sections = parse_sections(body)
        item = {
            "command": cmd,
            "syntax": sections["Syntax"],
            "hierarchy_level": sections["Hierarchy Level"],
            "description": sections["Description"],
            "options": parse_options(sections["Options"]),
            "required_privilege_level": sections["Required Privilege Level"],
            "release_information": sections["Release Information"],
            "related_documentation": clean_related(sections["RELATED DOCUMENTATION"])
        }
        items.append(item)
    return items

def write_jsonl(items, out_path):
    with open(out_path, "w", encoding="utf-8") as f:
        for x in items:
            f.write(json.dumps(x, ensure_ascii=False) + "\n")

def main():
    src = "junos_cli.txt"
    parts_dir = "parts"
    jsonl_dir = "jsonl"
    os.makedirs(jsonl_dir, exist_ok=True)

    part_files = split_txt_by_size_with_anchor(src, parts_dir, max_mb=10.0)

    for p in part_files:
        with open(p, "r", encoding="utf-8") as f:
            text = f.read()
        items = extract_commands(text)
        out_jsonl = os.path.join(jsonl_dir, os.path.basename(p).replace(".txt", ".jsonl"))
        write_jsonl(items, out_jsonl)
        print("written:", out_jsonl, "items:", len(items))

if __name__ == "__main__":
    main()
