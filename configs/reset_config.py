import json
from pathlib import Path

def main():
    templates = Path(__file__).resolve().parent / "templates"

    for template in templates.glob("*.json"):
        with open(template, "r") as f:
            data = json.load(f)

        config_folder = Path(__file__).resolve().parent / template.name

        with open(config_folder, "w") as f:
            json.dump(data, f)




