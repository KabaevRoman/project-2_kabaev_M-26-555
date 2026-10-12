QUOTES = "\"'"
BOOL_VALUES = ("true", "false")


def split_outside_quotes(text, sep=","):
    """Делит строку по sep, не трогая разделители внутри кавычек."""
    parts, current, quote = [], "", None
    for ch in text:
        if quote:
            current += ch
            if ch == quote:
                quote = None
        elif ch in QUOTES:
            quote = ch
            current += ch
        elif ch == sep:
            parts.append(current)
            current = ""
        else:
            current += ch
    if quote:
        raise ValueError(f"Незакрытая кавычка: {text}")
    parts.append(current)
    return [p.strip() for p in parts]


def split_keyword(text, keyword):
    """Делит строку по слову-разделителю вне кавычек.

    Возвращает (до, после) или None, если слова нет.
    """
    lowered = text.lower()
    size = len(keyword)
    quote = None
    for i, ch in enumerate(text):
        if quote:
            if ch == quote:
                quote = None
        elif ch in QUOTES:
            quote = ch
        elif (
            ch.isspace()
            and lowered[i + 1 : i + 1 + size] == keyword
            and text[i + 1 + size : i + 2 + size].isspace()
        ):
            return text[:i].strip(), text[i + 1 + size :].strip()
    return None


def parse_value(token):
    """Строки — только в кавычках; true/false — bool; иначе целое число."""
    token = token.strip()
    if len(token) >= 2 and token[0] == token[-1] and token[0] in QUOTES:
        return token[1:-1]
    if token.lower() in BOOL_VALUES:
        return token.lower() == "true"
    digits = token[1:] if token.startswith("-") else token
    if digits.isdecimal():
        return int(token)
    raise ValueError(token)


def parse_values(text):
    """Разбирает список значений 'a, "b", 3' в список Python-значений."""
    return [parse_value(t) for t in split_outside_quotes(text)]


def parse_clause(text):
    """'age = 28, name = "Bob"' -> {'age': 28, 'name': 'Bob'}."""
    result = {}
    for part in split_outside_quotes(text):
        name, sep, value = part.partition("=")
        name = name.strip()
        if not sep or not name.isidentifier():
            raise ValueError(part)
        result[name] = parse_value(value)
    return result


def _strip_prefix(text, words):
    """Отбрасывает ведущие слова команды (без учёта регистра)."""
    parts = text.split(None, len(words))
    if len(parts) <= len(words):
        raise ValueError(text)
    if [p.lower() for p in parts[: len(words)]] != words:
        raise ValueError(text)
    return parts[len(words)]


def _single_name(text, source):
    """Проверяет, что в text ровно одно слово (имя таблицы)."""
    name = text.strip()
    if not name or len(name.split()) != 1:
        raise ValueError(source)
    return name


def parse_insert(text):
    """'insert into T values (...)' -> (имя_таблицы, список_значений)."""
    rest = _strip_prefix(text, ["insert", "into"])
    table, _, tail = rest.partition(" ")
    tail = tail.strip()
    keyword = "values"
    if not table or not tail.lower().startswith(keyword):
        raise ValueError(text)
    body = tail[len(keyword) :].strip()
    if not (body.startswith("(") and body.endswith(")")):
        raise ValueError(text)
    return table, parse_values(body[1:-1])


def parse_select(text):
    """'select from T [where ...]' -> (имя_таблицы, условие_или_None)."""
    rest = _strip_prefix(text, ["select", "from"])
    parts = split_keyword(rest, "where")
    if parts is None:
        return _single_name(rest, text), None
    table, where = parts
    if not where:
        raise ValueError(text)
    return _single_name(table, text), where


def parse_update(text):
    """'update T set ... where ...' -> (таблица, set_условие, where_условие)."""
    rest = _strip_prefix(text, ["update"])
    table, _, tail = rest.partition(" ")
    tail = tail.strip()
    if not table or not tail.lower().startswith("set") or not tail[3:4].isspace():
        raise ValueError(text)
    parts = split_keyword(tail[3:].strip(), "where")
    if parts is None or not parts[0] or not parts[1]:
        raise ValueError(text)
    return table, parts[0], parts[1]


def parse_delete(text):
    """'delete from T where ...' -> (имя_таблицы, условие)."""
    rest = _strip_prefix(text, ["delete", "from"])
    parts = split_keyword(rest, "where")
    if parts is None or not parts[1]:
        raise ValueError(text)
    return _single_name(parts[0], text), parts[1]


def parse_info(text):
    """'info T' -> имя_таблицы."""
    return _single_name(_strip_prefix(text, ["info"]), text)
