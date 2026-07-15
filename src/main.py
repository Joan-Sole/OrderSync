from asyncio.log import logger

from core import settings
from core.settings import load_settings
from core.logger import initialise_logger
from core.sqlserver import SqlServerConnection
from core.hyperfile import HyperFileConnection

def main() -> None:
	settings = load_settings("config/config.yaml")

	print(settings.application.name)
	print(settings.application.version)
	print(settings.application.frozen_months)
	print(settings.hyperfile.provider)
	print(settings.hyperfile.repository)
	print(settings.sqlserver.server)
	print(settings.sqlserver.database)

	logger = initialise_logger(settings)

	logger.info("Connecting to Hyperfile")
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
	
	with HyperFileConnection(settings) as hyper:
		command = hyper.connection.Execute(
			"SELECT COUNT(*) AS TOTAL FROM COMMANDE"
		)

		recordset = command[0]
		total = recordset.Fields("TOTAL").Value

		logger.info("Orders found in HyperFile: %s", total)

		recordset.Close()

	logger.info("HyperFile connection closed.")

if __name__ == "__main__":
	main()