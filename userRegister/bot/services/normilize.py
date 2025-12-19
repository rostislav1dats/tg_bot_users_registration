def normalize(value: str | None) -> str | None:
    if value:
        value = value.strip()
        return value if value else None
    return None