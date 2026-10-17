import os
import re


def clear():
    """Clear the terminal screen for Linux/macOS and Windows."""
    os.system("clear" if os.name == "posix" else "cls")


def grab_extension(text) -> str | None:
    """Extract a file extension from a given string."""
    pattern = r"\.([a-zA-Z0-9]{2,})$"

    match = re.search(pattern, text)

    if match:
        return match.group(1)
