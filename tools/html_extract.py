import re


def extract_flag(html) -> str | None:
    """
    Extract META{} flag from HTML string.
    """
    pattern = r'META\{[^}]+\}'
    match = re.search(pattern, html)
    if match:
        return match.group(0)
    return None
