import re
import os


def clear():
    os.system("clear" if os.name == "posix" else "cls")


def grab_extension(text) -> str | None:
    pattern = r"\.([^\d\]+)"

    match = re.search(pattern, text)

    if match:
        return match.group(1)
