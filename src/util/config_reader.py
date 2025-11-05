import os
import toml
from dotenv import load_dotenv
from loguru import logger

class ConfigLoader:

    ### initialize and reload config ###

    def __init__(self, config_path='config/config.toml') -> None:
        self._config_path = config_path
        self.reload()

    def reload(self, config_path: str = None) -> None:
        if config_path is None:
            config_path = self._config_path

        # load toml, env vlaues, cache files and create flattend config
        self._config = self._load_toml(config_path)
        self._load_env()
        self._add_cache_config()
        self._config_keys = self._flatten_dict(self._config)

    ### load tomel file ###

    # load the toml file
    def _load_toml(self, path: str) -> dict:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Configuration file not found: {path}")

        with open(path, "r", encoding="utf-8") as file:
            return toml.load(file)

    # flatten the tomel key by chnining them together with an underscore "_"
    def _flatten_dict(self, data, parent_key: str="", sep: str="_") -> dict:
        items = {}
        for key, value in data.items():
            new_key = f"{parent_key}{sep}{key}" if parent_key else key
            if isinstance(value, dict):
                items.update(self._flatten_dict(value, new_key, sep=sep))
            else:
                items[new_key] = value
        return items
    
    
    ### load chace files ###

    # recursivley merge dictionarys without overwriting existing keys
    def _merge_dict_no_overwrite(self, base: dict, updates: dict, wrap_key: str | None = None):

        # Handle wrap_key if provided (put key infront of evry merged key)
        if wrap_key:
            if wrap_key not in base:
                base[wrap_key] = updates
            elif isinstance(base[wrap_key], dict):
                self._merge_dict_no_overwrite(base[wrap_key], updates)
            return

        # Normal recursive merge
        for key, value in updates.items():
            if key not in base:
                base[key] = value
            elif isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_dict_no_overwrite(base[key], value)
            
    # add cache files to the config by merging them into self._config
    def _add_cache_config(self) -> None:
        cahe_paths = self._config["GENENERAL_CONFIGURATION"]["CACHE_FILES"]

        for cache_path in cahe_paths:
            try:
                cache_keys = self._load_toml(cache_path)
                self._merge_dict_no_overwrite(self._config, cache_keys, wrap_key="CACHE")
            except FileNotFoundError:
                logger.warning(f"Cache file not found: {cache_path}")
    


    ### load env files ###
    
    # load env values based on the configured env values in the toml file
    def _load_env(self) -> None:
        load_dotenv()
        try:
            for key in self._config ["GENENERAL_CONFIGURATION"]["ENV_VALUES"]:
                self._config[key] = os.getenv(key)
        except KeyError:
            logger.warning("No ENV_VALUES section found in configuration.")

    
    ### output config ###
    
    # retun all values as dictionary
    def to_dict(self) -> dict:
        self._config_keys = self._flatten_dict(self._config)
        return self._config_keys.copy()
    
