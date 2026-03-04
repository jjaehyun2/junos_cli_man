import os

def split_txt_by_size_with_anchor(src, out_dir, max_mb=9.5, anchor="IN THIS SECTION"):
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

    for i, part in enumerate(parts, 1):
        out_path = os.path.join(out_dir, f"junos_cli_part_{i:03d}.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(part)
        print("written:", out_path, len(part))

# 사용 예시
# split_txt_by_size_with_anchor("junos_cli_2220_32857.txt", "./parts", max_mb=9.5)
