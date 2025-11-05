import os
import toml
from dotenv import load_dotenv
from loguru import logger

class ConfigLoader:

    """
    Configuration loader to manage toml config file, env keys and toml chache files. 
    To crate it, you have to provide the path to the toml config file.

    Methods to interact with:
        - reload: reloads the config file and env values, as well as the cache files
        - cache values: this method, allows you to cache key value pairs -> provide the key in a "_" splitted form, e.g. "SECTION_SUBSECTION_KEY"
        - to_dict: returns the full config as a flatend dictionary
    """

    ### initialize and reload config ###

    def __init__(self, config_path='config/config.toml') -> None:
        self._config_path = config_path
        self.reload()

        logger.info(f"✅ Configuration loaded from {config_path}")

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
    def _merge_dict_no_overwrite(self, base: dict, updates: dict, wrap_key: str | None = None) -> None:

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
        
        for _, cache_path in cahe_paths.items():
            try:
                cache_keys = self._load_toml(cache_path)
                self._merge_dict_no_overwrite(self._config, cache_keys, wrap_key="CACHE")
            except FileNotFoundError:
                logger.warning(f"Cache file not found: {cache_path}")
    
    # cache multiple values to a toml file by file path and list of (key, value) pairs
    def cache_values(self, path: str, items: list[tuple[str, object]], split_char: str | None = "_", split: bool = True) -> None:
        if not isinstance(items, list):
            raise TypeError("items must be a list of (key, value) pairs")

        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write("")

        data = self._load_toml(path)

        for key_path, value in items:
            if not isinstance(key_path, str):
                raise TypeError("Each key must be a string")

            if split and split_char is not None:
                parts = key_path.split(split_char)
            else:
                parts = [key_path]

            current = data
            for part in parts[:-1]:
                if part not in current or not isinstance(current[part], dict):
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = value

        with open(path, "w", encoding="utf-8") as f:
            toml.dump(data, f)

        self.reload()
        logger.info(f"Cached {len(items)} items to {path}")


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