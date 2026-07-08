from core.settings import load_settings


def main() -> None:
    settings = load_settings("config/config.yaml")

    print(settings.application.name)
    print(settings.application.version)
    print(settings.application.frozen_months)
    print(settings.hyperfile.dsn)
    print(settings.sqlserver.server)
    print(settings.sqlserver.database)


if __name__ == "__main__":
    main()