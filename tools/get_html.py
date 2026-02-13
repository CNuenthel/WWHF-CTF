import requests


def get_html(url, timeout=10):
    """
    Simple HTML fetcher

    Args:
        url: Target URL
        timeout: Request timeout in seconds

    Returns:
        HTML content as string or None if failed
    """
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()  # Raise exception for bad status codes
        return response.text
    except Exception as e:
        print(f"[!] Error fetching {url}: {e}")
        return None