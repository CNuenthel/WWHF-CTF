import re


def extract_flag(html) -> str | None:
    """
    Extract MetaCTF flag from HTML string.

    Args:
        html: String containing HTML content

    Returns:
        The flag string (e.g., "MetaCTF{...}") or None if not found
    """
    # Match MetaCTF{ followed by any characters until the closing }
    pattern = r'MetaCTF\{[^}]+\}'

    match = re.search(pattern, html)

    if match:
        return match.group(0)
    return None


# Alternative version that handles edge cases
def extract_flag_robust(html) -> str | None:
    """
    More robust flag extraction that handles HTML entities and nested braces
    """
    # First, decode HTML entities if present
    import html as html_module
    html = html_module.unescape(html)

    # This handles cases where there might be multiple } characters
    pattern = r'MetaCTF\{[^}]*\}'

    match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)

    if match:
        return match.group(0)
    return None


# Version that finds ALL flags if multiple exist
def extract_all_flags(html) -> list | None:
    """
    Extract all MetaCTF flags from HTML (in case there are multiple)

    Returns:
        List of flag strings
    """
    import html as html_module
    html = html_module.unescape(html)
    pattern = r'MetaCTF\{[^}]+\}'
    flags = re.findall(pattern, html, re.IGNORECASE)
    return flags if flags else None
