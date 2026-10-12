import json
import os

from primitive_db.constants import DATA_DIR


def load_metadata(filepath):
    """Загружает метаданные из JSON; при отсутствии файла возвращает {}."""
    try:
        with open(filepath, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_metadata(filepath, data):
    """Сохраняет метаданные в JSON-файл."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def _table_path(table_name):
    """Путь к файлу данных таблицы."""
    return os.path.join(DATA_DIR, f"{table_name}.json")


def load_table_data(table_name):
    """Загружает записи таблицы; при отсутствии файла возвращает []."""
    try:
        with open(_table_path(table_name), encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_table_data(table_name, data):
    """Сохраняет записи таблицы в data/<таблица>.json."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(_table_path(table_name), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def delete_table_data(table_name):
    """Удаляет файл данных таблицы, если он есть."""
    try:
        os.remove(_table_path(table_name))
    except FileNotFoundError:
        pass
