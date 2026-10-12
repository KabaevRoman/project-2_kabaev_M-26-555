# primitive_db

Консольное приложение, имитирующее работу с примитивной базой данных.

## Запуск

```
uv sync
uv run project
```

## Управление таблицами

Команды:

- `create_table <имя> <столбец:тип> ...` — создать таблицу (типы: `int`, `str`, `bool`; столбец `ID:int` добавляется автоматически)
- `list_tables` — список таблиц
- `drop_table <имя>` — удалить таблицу
- `help` — справка
- `exit` — выход

Метаданные хранятся в `db_meta.json` в текущей директории.

Пример:

```
>>>Введите команду: create_table users name:str age:int is_active:bool
Таблица "users" успешно создана со столбцами: ID:int, name:str, age:int, is_active:bool
>>>Введите команду: list_tables
- users
>>>Введите команду: drop_table users
Таблица "users" успешно удалена.
```
