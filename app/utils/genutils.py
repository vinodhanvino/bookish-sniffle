def safe_get(d: dict, key: str, defaultValue='', separator='||'):
    if not (d):
        return defaultValue
    parts = key.split(separator)
    current = d
    for part in parts:
        if not (current):
            return defaultValue
        current = current[part]
        if isinstance(current, str) and not (current):
            return defaultValue

    return current
