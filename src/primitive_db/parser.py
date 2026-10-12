import re


class ParseError(ValueError):
    """Некорректное значение в команде; текст — сам проблемный фрагмент."""


_CLAUSE_RE = re.compile(r"^\s*(\w+)\s*=\s*(.+?)\s*$")
_INT_RE = re.compile(r"^-?\d+$")


def split_outside_quotes(text, sep=","):
    """Делит строку по sep, не трогая разделители внутри кавычек."""
    parts, current, quote = [], "", None
    for ch in text:
        if quote:
            current += ch
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
            current += ch
        elif ch == sep:
            parts.append(current)
            current = ""
        else:
            current += ch
    if quote:
        raise ParseError(f"Незакрытая кавычка: {text}")
    parts.append(current)
    return [p.strip() for p in parts]


def parse_value(token):
    """Строки — только в кавычках; true/false — bool; иначе целое число."""
    token = token.strip()
    if len(token) >= 2 and token[0] == token[-1] and token[0] in "\"'":
        return token[1:-1]
    if token.lower() in ("true", "false"):
        return token.lower() == "true"
    if _INT_RE.match(token):
        return int(token)
    raise ParseError(token)


def parse_values(text):
    """Разбирает список значений 'a, "b", 3' в список Python-значений."""
    return [parse_value(t) for t in split_outside_quotes(text)]


def parse_clause(text):
    """'age = 28, name = "Bob"' -> {'age': 28, 'name': 'Bob'}."""
    result = {}
    for part in split_outside_quotes(text):
        match = _CLAUSE_RE.match(part)
        if not match:
            raise ParseError(part)
        result[match.group(1)] = parse_value(match.group(2))
    return result
