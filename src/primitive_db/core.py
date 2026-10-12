from primitive_db.decorators import confirm_action, handle_db_errors, log_time

VALID_TYPES = ("int", "str", "bool")

TYPE_CHECKS = {
    "int": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "str": lambda v: isinstance(v, str),
    "bool": lambda v: isinstance(v, bool),
}


def get_columns(metadata, table_name):
    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует.')
    return {c["name"]: c["type"] for c in metadata[table_name]["columns"]}


def find_records(table_data, where_clause):
    """Записи, подходящие под условие (без условия — все)."""
    if not where_clause:
        return table_data
    return [
        r
        for r in table_data
        if all(r.get(k) == v for k, v in where_clause.items())
    ]


@handle_db_errors
def create_table(metadata, table_name, columns):
    """Создаёт таблицу; ID:int добавляется первым столбцом автоматически.

    columns — список пар (имя, тип).
    """
    if table_name in metadata:
        raise ValueError(f'Таблица "{table_name}" уже существует.')

    for name, col_type in columns:
        if col_type not in VALID_TYPES:
            raise ValueError(f"Неподдерживаемый тип {name}:{col_type}.")

    metadata[table_name] = {
        "columns": [{"name": "ID", "type": "int"}]
        + [{"name": n, "type": t} for n, t in columns]
    }
    all_columns = metadata[table_name]["columns"]
    cols = ", ".join(f"{c['name']}:{c['type']}" for c in all_columns)
    print(f'Таблица "{table_name}" успешно создана со столбцами: {cols}')
    return metadata


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует.')

    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


def list_tables(metadata):
    if not metadata:
        print("Таблиц нет.")
    for name in metadata:
        print(f"- {name}")


def validate_clause_types(columns, record):
    for name, value in record.items():
        if not TYPE_CHECKS[columns[name]](value):
            raise ValueError(
                f"Значение {value!r} не подходит для столбца "
                f'"{name}" (ожидается {columns[name]}).'
            )


@handle_db_errors
def validate_clause(metadata, table_name, clause):
    """Проверяет таблицу, столбцы и типы значений. True, если всё верно."""
    columns = get_columns(metadata, table_name)
    for name in clause:
        if name not in columns:
            raise ValueError(f'Столбец "{name}" не существует.')
    validate_clause_types(columns, clause)
    return True


@handle_db_errors
def table_info(metadata, table_name, table_data):
    columns = get_columns(metadata, table_name)
    cols = ", ".join(f"{n}:{t}" for n, t in columns.items())
    return cols, len(table_data)


@handle_db_errors
@log_time
def insert(metadata, table_name, values, table_data):
    columns = get_columns(metadata, table_name)
    names = [n for n in columns if n != "ID"]
    if len(values) != len(names):
        raise ValueError(
            f"Ожидается значений: {len(names)}, передано: {len(values)}."
        )

    record = dict(zip(names, values))
    validate_clause_types(columns, record)

    new_id = max((r["ID"] for r in table_data), default=0) + 1
    table_data.append({"ID": new_id, **record})
    return table_data


@handle_db_errors
@log_time
def select(table_data, where_clause=None):
    return find_records(table_data, where_clause)


@handle_db_errors
def update(table_data, set_clause, where_clause):
    if "ID" in set_clause:
        raise ValueError("Столбец ID изменять нельзя.")
    found = find_records(table_data, where_clause)
    if not found:
        raise ValueError("Записи по условию не найдены.")
    for record in found:
        record.update(set_clause)
    return table_data


@handle_db_errors
@confirm_action("удаление записи")
def delete(table_data, where_clause):
    found = find_records(table_data, where_clause)
    if not found:
        raise ValueError("Записи по условию не найдены.")
    return [r for r in table_data if r not in found]
