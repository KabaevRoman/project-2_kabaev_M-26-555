import json
import os


def load_metadata(filepath):
    try:
        with open(filepath, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_metadata(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


DATA_DIR = "data"


def _table_path(table_name):
    return os.path.join(DATA_DIR, f"{table_name}.json")


def load_table_data(table_name):
    try:
        with open(_table_path(table_name), encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_table_data(table_name, data):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(_table_path(table_name), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def delete_table_data(table_name):
    try:
        os.remove(_table_path(table_name))
    except FileNotFoundError:
        pass
