
def camel_to_snake(name: str) -> str:
    """将 camelCase 字符串转换为 snake_case 字符串"""
    if "_" in name:
        return name
    import re

    name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    name = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", name)
    name = name.replace("-", "_").lower()
    return name

def snake_to_camel(name: str, capital: bool = False) -> str:
    """将 snake_case 字符串转换为 camelCase 字符串"""
    name = "".join(seg.capitalize() for seg in name.split("_"))
    if not capital:
        name = name[0].lower() + name[1:]
    return name