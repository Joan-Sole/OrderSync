from dataclasses import dataclass
from pathlib import Path
import yaml


@dataclass
class ApplicationConfig:
    name: str
    version: str
    frozen_months: int
    log_directory: str


@dataclass
class HyperFileConfig:
    dsn: str
    user: str
    password: str


@dataclass
class SqlServerConfig:
    server: str
    database: str
    trusted_connection: bool


@dataclass
class Settings:
    application: ApplicationConfig
    hyperfile: HyperFileConfig
    sqlserver: SqlServerConfig


def load_settings(config_path: str | Path) -> Settings:
    config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    return Settings(
        application=ApplicationConfig(**data["application"]),
        hyperfile=HyperFileConfig(**data["hyperfile"]),
        sqlserver=SqlServerConfig(**data["sqlserver"]),
    )