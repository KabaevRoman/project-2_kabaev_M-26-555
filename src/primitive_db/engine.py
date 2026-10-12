import shlex

import prompt

from primitive_db.core import create_table, drop_table, list_tables
from primitive_db.utils import load_metadata, save_metadata

META_FILE = "db_meta.json"


def print_help():
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def parse_columns(specs):
    columns = []
    for spec in specs:
        name, sep, col_type = spec.partition(":")
        if not sep or not name or not col_type:
            print(f"Некорректное значение: {spec}. Попробуйте снова.")
            return None
        columns.append((name, col_type))
    return columns


def run():
    print_help()

    while True:
        metadata = load_metadata(META_FILE)
        user_input = prompt.string(">>>Введите команду: ")

        try:
            args = shlex.split(user_input)
        except ValueError:
            print(f"Некорректное значение: {user_input}. Попробуйте снова.")
            continue
        if not args:
            continue

        command = args[0]
        match command:
            case "exit":
                break
            case "help":
                print_help()
            case "list_tables":
                list_tables(metadata)
            case "create_table":
                if len(args) < 2:
                    print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                    continue
                columns = parse_columns(args[2:])
                if columns is None:
                    continue
                new_meta = create_table(metadata, args[1], columns)
                save_metadata(META_FILE, new_meta)
            case "drop_table":
                if len(args) != 2:
                    print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                    continue
                new_meta = drop_table(metadata, args[1])
                save_metadata(META_FILE, new_meta)
            case _:
                print(f"Функции {command} нет. Попробуйте снова.")
