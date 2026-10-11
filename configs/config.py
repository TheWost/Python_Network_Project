import json
from pathlib import Path


class Config:
    def __init__(self, config_name: str):
        self.CONFIGS = {
            "tui_config": "tui_config.json",
            "server_config": "server_config.json",
        }

        if config_name not in self.CONFIGS:
            raise ValueError(
                f"Unknown config '{config_name}'. "
                f"Valid options: {', '.join(self.CONFIGS)}"
            )

        self.configs_directory = Path(__file__).resolve().parent

        if not self.configs_directory.exists():
            raise FileNotFoundError(
                "Configs folder doesn't exist! "
                "Please copy it from the repo folder or redownload the whole repo."
            )

        self.config_path = self.configs_directory / self.CONFIGS[config_name]

        if not self.config_path.exists():
            raise FileNotFoundError(f"{config_name} is missing!")

    def load_data(self) -> dict:
        with self.config_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def write_data(self, data: dict) -> None:
        with self.config_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
