from core.settings import load_settings
from core.logger import initialise_logger

def main() -> None:
    settings = load_settings("config/config.yaml")

    print(settings.application.name)
    print(settings.application.version)
    print(settings.application.frozen_months)
    print(settings.hyperfile.dsn)
    print(settings.sqlserver.server)
    print(settings.sqlserver.database)

    logger = initialise_logger(settings)

    logger.info("Application started.")
    logger.warning("This is a warning.")
    logger.error("This is an error.")
    logger.info("Application finished.")
    
if __name__ == "__main__":
    main()