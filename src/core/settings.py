"""
OrderSync

Module:
    settings.py
    
Location:
    src\\core

Description:
    Loads and validates application configuration from YAML.

Version:
    1.0.0
"""

from dataclasses import dataclass
from pathlib import Path
from .exceptions import ConfigurationError

import yaml
import logging

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class ApplicationConfig:
    name: str
    version: str
    log_directory: str
    log_level: str
    maj_periode: int


@dataclass(frozen=True)
class HyperFileConfig:
    provider: str
    repository: str
    password: str


@dataclass(frozen=True)
class SqlServerConfig:
    server: str
    database: str
    driver: str = "ODBC Driver 18 for SQL Server"
    trusted_connection: bool = True
    username: str = ""
    password: str = ""
    timeout: int = 30


@dataclass(frozen=True)
class Settings:
    application: ApplicationConfig
    hyperfile: HyperFileConfig
    sqlserver: SqlServerConfig
    

def load_settings(config_path: str | Path) -> Settings:
    """
    Load application settings from a YAML configuration file.
    """
    path = Path(config_path)

    if not path.exists():
        raise ConfigurationError(
            f"Configuration file not found: {path}"
        )

    try:
        with path.open("r", encoding="utf-8") as file:
            data = yaml.safe_load(file)

        if data is None:
            raise ConfigurationError(
                f"Configuration file is empty: {path}"
            )

        return Settings(
            application=ApplicationConfig(**data["application"]),
            hyperfile=HyperFileConfig(**data["hyperfile"]),
            sqlserver=SqlServerConfig(**data["sqlserver"]),
        )

    except ConfigurationError:
        raise

    except KeyError as exc:
        raise ConfigurationError(
            f"Missing configuration key: {exc}"
        ) from exc

    except TypeError as exc:
        raise ConfigurationError(
            f"Invalid configuration parameter: {exc}"
        ) from exc

    except yaml.YAMLError as exc:
        raise ConfigurationError(
            f"Invalid YAML configuration: {exc}"
        ) from exc

    except OSError as exc:
        raise ConfigurationError(
            f"Unable to read configuration file: {exc}"
        ) from exc
