import os
import toml
from dotenv import load_dotenv
from loguru import logger

class ConfigLoader:
    """
    Manages configuration loading from TOML files, environment variables, and cache files.
    """

    def __init__(self, config_path='config/config.toml') -> None:
        """Initialize with config path and load configuration."""
        self._config_path = config_path
        self.reload()

        logger.info(f"✅ Configuration loaded from {config_path}")

    def reload(self, config_path: str = None) -> None:
        """Reloads configuration, env variables, and cache."""
        if config_path is None:
            config_path = self._config_path

        self._config = self._load_toml(config_path)
        self._load_env()
        self._add_cache_config()
        self._config_keys = self._flatten_dict(self._config)

    def _load_toml(self, path: str) -> dict:
        """Loads and parses a TOML file."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Configuration file not found: {path}")

        with open(path, "r", encoding="utf-8") as file:
            return toml.load(file)

    def _flatten_dict(self, data, parent_key: str="", sep: str="_") -> dict:
        """Flattens a nested dictionary into a single level with separator-joined keys."""
        items = {}
        for key, value in data.items():
            new_key = f"{parent_key}{sep}{key}" if parent_key else key
            if isinstance(value, dict):
                items.update(self._flatten_dict(value, new_key, sep=sep))
            else:
                items[new_key] = value
        return items
    
    def _merge_dict_no_overwrite(self, base: dict, updates: dict, wrap_key: str | None = None) -> None:
        """Recursively merges updates into base dictionary without overwriting existing keys."""
        if wrap_key:
            if wrap_key not in base:
                base[wrap_key] = updates
            elif isinstance(base[wrap_key], dict):
                self._merge_dict_no_overwrite(base[wrap_key], updates)
            return

        for key, value in updates.items():
            if key not in base:
                base[key] = value
            elif isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_dict_no_overwrite(base[key], value)
            
    def _add_cache_config(self) -> None:
        """Merges cache files defined in configuration into the main config."""
        cahe_paths = self._config["GENENERAL_CONFIGURATION"]["CACHE_FILES"]
        
        for _, cache_path in cahe_paths.items():
            try:
                cache_keys = self._load_toml(cache_path)
                self._merge_dict_no_overwrite(self._config, cache_keys, wrap_key="CACHE")
            except FileNotFoundError:
                logger.warning(f"Cache file not found: {cache_path}")
    
    def cache_values(self, path: str, items: list[tuple[str, object]], split_char: str | None = "_", split: bool = True) -> None:
        """Writes key-value pairs to a TOML cache file, optionally splitting keys by separator."""
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

    def _load_env(self) -> None:
        """Loads environment variables specified in config into the configuration dictionary."""
        load_dotenv()
        try:
            for key in self._config ["GENENERAL_CONFIGURATION"]["ENV_VALUES"]:
                self._config[key] = os.getenv(key)
        except KeyError:
            logger.warning("No ENV_VALUES section found in configuration.")

    def to_dict(self) -> dict:
        """Returns the flattened configuration dictionary."""
        self._config_keys = self._flatten_dict(self._config)
        return self._config_keys.copy()