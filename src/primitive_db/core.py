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


TYPE_CHECKS = {
    "int": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "str": lambda v: isinstance(v, str),
    "bool": lambda v: isinstance(v, bool),
}


def get_columns(metadata, table_name):
    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует.')
    return {c["name"]: c["type"] for c in metadata[table_name]["columns"]}


def validate_clause(metadata, table_name, clause):
    """Проверяет, что столбцы существуют и типы значений им соответствуют."""
    columns = get_columns(metadata, table_name)
    for name, value in clause.items():
        if name not in columns:
            raise ValueError(f'Столбец "{name}" не существует.')
        if not TYPE_CHECKS[columns[name]](value):
            raise ValueError(
                f'Значение {value!r} не подходит для столбца "{name}" '
                f"(ожидается {columns[name]})."
            )


def insert(metadata, table_name, values, table_data):
    columns = get_columns(metadata, table_name)
    names = [n for n in columns if n != "ID"]
    if len(values) != len(names):
        raise ValueError(
            f"Ожидается значений: {len(names)}, передано: {len(values)}."
        )

    record = dict(zip(names, values))
    validate_clause(metadata, table_name, record)

    new_id = max((r["ID"] for r in table_data), default=0) + 1
    table_data.append({"ID": new_id, **record})
    return table_data


def _matches(record, where_clause):
    return all(record.get(k) == v for k, v in where_clause.items())


def select(table_data, where_clause=None):
    if not where_clause:
        return table_data
    return [r for r in table_data if _matches(r, where_clause)]


def update(table_data, set_clause, where_clause):
    for record in table_data:
        if _matches(record, where_clause):
            record.update(set_clause)
    return table_data


def delete(table_data, where_clause):
    return [r for r in table_data if not _matches(r, where_clause)]
