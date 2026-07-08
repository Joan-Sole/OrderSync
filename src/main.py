from settings import load_settings


def main() -> None:
    settings = load_settings("config/config.yaml")

    print(settings.application.name)
    print(settings.application.version)
    print(settings.hyperfile.dsn)
    print(settings.sqlserver.server)


if __name__ == "__main__":
    main()