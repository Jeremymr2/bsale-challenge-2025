def snake_to_camel(snake_str: str) -> str:
    """Convierte snake_case a camelCase."""
    components = snake_str.split('_')
    return components[0] + ''.join(word.capitalize() for word in components[1:])