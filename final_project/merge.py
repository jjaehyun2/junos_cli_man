import json
from pathlib import Path

def merge_jsonl_files():
    
    jsonl_dir = Path("jsonl")
    
    input_files = [
        "junos_cli_part_001.jsonl",
        "junos_cli_part_002.jsonl",
        "junos_cli_part_003.jsonl",
        "junos_cli_part_004.jsonl"
    ]
    
    output_file = Path("junos_command.jsonl")
    
    with open(output_file, 'w', encoding='utf-8') as outf:
        for file_name in input_files:
            file_path = jsonl_dir / file_name
            print(f"Processing: {file_path}")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as inf:
                    
                    for line in inf:
                        line = line.strip()
                        if line:
                            outf.write(line + '\n')
                print(f" {file_name} merged successfully")
            except FileNotFoundError:
                print(f" {file_path} not found")
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
    
    print(f"\n Merge complete! Output file: {output_file}")

if __name__ == "__main__":
    merge_jsonl_files()
