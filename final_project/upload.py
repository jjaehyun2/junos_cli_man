from datasets import load_dataset

dataset = load_dataset("json", data_files="./folder/train.jsonl")
dataset.push_to_hub("jack0503/junos_cli_manual")