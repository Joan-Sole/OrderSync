from asyncio.log import logger

from core import settings
from core.settings import load_settings
from core.logger import initialise_logger
from core.sqlserver import SqlServerConnection

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
	
	settings = load_settings("config/config.yaml")
	logger = initialise_logger(settings)

	sql = SqlServerConnection(settings)
	logger.info("Connecting SQL Server...")
	sql.connect()
	logger.info("SQL Server connected.")
	cursor = sql.connection.cursor()
	cursor.execute("SELECT @@VERSION")
	row = cursor.fetchone()
	logger.info(row[0])
	cursor.close()
	sql.disconnect()
	logger.info("Disconnected.")
	logger.info(row[0])
 
if __name__ == "__main__":
	main()