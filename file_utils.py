import json
import os

def dump_json_to_file(data: dict, folder_name: str, file_name: str, **kwargs):
    if not os.path.isdir(folder_name):
        raise ValueError(f"`{folder_name}` is not a valid directory!")
    file_path = os.path.join(folder_name, file_name)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4, **kwargs)