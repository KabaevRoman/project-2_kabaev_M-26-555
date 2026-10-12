import re
import shlex

import prompt
from prettytable import PrettyTable

from primitive_db import core
from primitive_db.parser import ParseError, parse_clause, parse_values
from primitive_db.utils import (
    delete_table_data,
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)

META_FILE = "db_meta.json"

INSERT_RE = re.compile(
    r"^insert\s+into\s+(\w+)\s+values\s*\((.*)\)\s*$", re.IGNORECASE
)
SELECT_RE = re.compile(
    r"^select\s+from\s+(\w+)(?:\s+where\s+(.+))?\s*$", re.IGNORECASE
)
UPDATE_RE = re.compile(
    r"^update\s+(\w+)\s+set\s+(.+?)\s+where\s+(.+)$", re.IGNORECASE
)
DELETE_RE = re.compile(r"^delete\s+from\s+(\w+)\s+where\s+(.+)$", re.IGNORECASE)
INFO_RE = re.compile(r"^info\s+(\w+)\s*$", re.IGNORECASE)


def print_help():
    """Prints the help message for the current mode."""

    print("\n***Операции с данными***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("<command> insert into <имя_таблицы> values (<значение1>, ...)")
    print("    - создать запись")
    print("<command> select from <имя_таблицы> [where <столбец> = <значение>]")
    print("    - прочитать записи")
    print("<command> update <имя_таблицы> set <столбец> = <значение>")
    print("    where <столбец> = <значение> - обновить запись")
    print("<command> delete from <имя_таблицы> where <столбец> = <значение>")
    print("    - удалить запись")
    print("<command> info <имя_таблицы> - вывести информацию о таблице")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def parse_columns(specs):
    """Разбирает 'имя:тип' в пары; возвращает None при некорректной записи."""
    columns = []
    for spec in specs:
        name, sep, col_type = spec.partition(":")
        if not sep or not name or not col_type:
            print(f"Некорректное значение: {spec}. Попробуйте снова.")
            return None
        columns.append((name, col_type))
    return columns


def print_table(metadata, table_name, records):
    if not records:
        print("Записей не найдено.")
        return
    names = [c["name"] for c in metadata[table_name]["columns"]]
    table = PrettyTable(names)
    for record in records:
        table.add_row([record[n] for n in names])
    print(table)


def format_ids(records):
    return ", ".join(str(r["ID"]) for r in records)


def handle_data_command(user_input, metadata):
    """Обрабатывает CRUD-команды. Возвращает False, если команда не распознана."""
    if m := INSERT_RE.match(user_input):
        table_name = m.group(1)
        core.get_columns(metadata, table_name)
        data = load_table_data(table_name)
        data = core.insert(metadata, table_name, parse_values(m.group(2)), data)
        save_table_data(table_name, data)
        print(
            f'Запись с ID={data[-1]["ID"]} успешно добавлена '
            f'в таблицу "{table_name}".'
        )
    elif m := SELECT_RE.match(user_input):
        table_name = m.group(1)
        core.get_columns(metadata, table_name)
        where = parse_clause(m.group(2)) if m.group(2) else None
        if where:
            core.validate_clause(metadata, table_name, where)
        data = load_table_data(table_name)
        print_table(metadata, table_name, core.select(data, where))
    elif m := UPDATE_RE.match(user_input):
        table_name = m.group(1)
        set_clause, where = parse_clause(m.group(2)), parse_clause(m.group(3))
        core.validate_clause(metadata, table_name, set_clause)
        core.validate_clause(metadata, table_name, where)
        if "ID" in set_clause:
            raise ValueError("Столбец ID изменять нельзя.")
        data = load_table_data(table_name)
        found = core.select(data, where)
        if not found:
            raise ValueError("Записи по условию не найдены.")
        ids = format_ids(found)
        save_table_data(table_name, core.update(data, set_clause, where))
        print(f'Запись с ID={ids} в таблице "{table_name}" успешно обновлена.')
    elif m := DELETE_RE.match(user_input):
        table_name = m.group(1)
        where = parse_clause(m.group(2))
        core.validate_clause(metadata, table_name, where)
        data = load_table_data(table_name)
        found = core.select(data, where)
        if not found:
            raise ValueError("Записи по условию не найдены.")
        ids = format_ids(found)
        save_table_data(table_name, core.delete(data, where))
        print(f'Запись с ID={ids} успешно удалена из таблицы "{table_name}".')
    elif m := INFO_RE.match(user_input):
        table_name = m.group(1)
        columns = core.get_columns(metadata, table_name)
        cols = ", ".join(f"{n}:{t}" for n, t in columns.items())
        print(f"Таблица: {table_name}")
        print(f"Столбцы: {cols}")
        print(f"Количество записей: {len(load_table_data(table_name))}")
    else:
        return False
    return True


def run():
    print_help()

    while True:
        metadata = load_metadata(META_FILE)
        user_input = prompt.string(">>>Введите команду: ").strip()
        if not user_input:
            continue

        try:
            if handle_data_command(user_input, metadata):
                continue
        except ParseError as e:
            print(f"Некорректное значение: {e}. Попробуйте снова.")
            continue
        except ValueError as e:
            print(f"Ошибка: {e}")
            continue

        try:
            args = shlex.split(user_input)
        except ValueError:
            print(f"Некорректное значение: {user_input}. Попробуйте снова.")
            continue

        command = args[0]
        match command:
            case "exit":
                break
            case "help":
                print_help()
            case "list_tables":
                core.list_tables(metadata)
            case "create_table":
                if len(args) < 2:
                    print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                    continue
                columns = parse_columns(args[2:])
                if columns is None:
                    continue
                save_metadata(
                    META_FILE, core.create_table(metadata, args[1], columns)
                )
            case "drop_table":
                if len(args) != 2:
                    print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                    continue
                existed = args[1] in metadata
                save_metadata(META_FILE, core.drop_table(metadata, args[1]))
                if existed:
                    delete_table_data(args[1])
            case _:
                print(f"Функции {command} нет. Попробуйте снова.")
