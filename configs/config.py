import json
from pathlib import Path


class Config:
    CONFIGS = {
        "tui_config": "tui_config.json",
        "server_config": "server_config.json",
    }

    def __init__(self, config_name: str):
        if config_name not in Config.CONFIGS:
            raise ValueError(
                f"Unknown config '{config_name}'. "
                f"Valid options: {', '.join(Config.CONFIGS)}"
            )

        self.configs_directory = Path(__file__).resolve().parent / "configs"

        if not self.configs_directory.exists():
            raise FileNotFoundError(
                "Configs folder doesn't exist! "
                "Please copy it from the repo folder or redownload the whole repo."
            )

        self.config_path = self.configs_directory / Config.CONFIGS[config_name]

        if not self.config_path.exists():
            raise FileNotFoundError(f"{config_name} is missing!")

    def load_data(self) -> dict:
        with self.config_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def write_data(self, data: dict) -> None:
        with self.config_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
