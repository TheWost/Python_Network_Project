import json
from pathlib import Path


class Config:
    def __init__(self, config_name):


        self.configs_directory = Path(__file__).resolve() / "configs"


        if not self.configs_directory.exists():
            raise FileNotFoundError("Configs folder dosen't exist! Please copy from repo folder or redownload whole repo.")


        self.configs = {
                        "tui_config": self.configs_directory / "tui_config.json",
                        "server_config": self.configs_directory / "server_config.json",
                        }
        self.config_path = Path(self.configs[config_name])
        if not self.config_path.exists():
            raise FileNotFoundError(f"{config_name} is missing!")

    def load_data(self):
        with open(self.config_path, "r") as f:
            return json.load(f)

    def write_data(self, data):
        with open(config_path, "w") as f:
            json.dump(data, f, indent=4)


