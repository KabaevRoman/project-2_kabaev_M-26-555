VALID_TYPES = ("int", "str", "bool")


def create_table(metadata, table_name, columns):
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata

    for name, col_type in columns:
        if col_type not in VALID_TYPES:
            print(f"Некорректное значение: {name}:{col_type}. Попробуйте снова.")
            return metadata

    metadata[table_name] = {
        "columns": [{"name": "ID", "type": "int"}]
        + [{"name": n, "type": t} for n, t in columns]
    }
    all_columns = metadata[table_name]["columns"]
    cols = ", ".join(f"{c['name']}:{c['type']}" for c in all_columns)
    print(f'Таблица "{table_name}" успешно создана со столбцами: {cols}')
    return metadata


def drop_table(metadata, table_name):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


def list_tables(metadata):
    if not metadata:
        print("Таблиц нет.")
    for name in metadata:
        print(f"- {name}")
