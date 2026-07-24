from asyncio.log import logger

from core.settings import load_settings
from core.logger import initialise_logger
from core.sqlserver import SqlServerConnection
from core.hyperfile import HyperFileConnection
from repositories.hyperfile_repository import HyperFileRepository

import time

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
		recordset = hyper.execute(
			"SELECT COUNT(*) AS TOTAL FROM COMMANDE"
		)

		total = recordset.Fields("TOTAL").Value

		logger.info("Orders found in HyperFile: %s", total)

		recordset.Close()

	logger.info("HyperFile connection closed.")


	started_at = time.perf_counter()

	order_count = 0
	line_count = 0
	orders_without_lines = 0

	print("Starting order synchronization...................................")

	with SqlServerConnection(settings) as sql:

		cursor = sql.execute(
	   		 "SELECT @@SERVERNAME, DB_NAME(), GETDATE()"
   		 )

		row = cursor.fetchone()

		logger.info("Server   : %s", row[0])
		logger.info("Database : %s", row[1])
		logger.info("Date     : %s", row[2])

		cursor.close()

	print("Starting order synchronization...................................")


	with SqlServerConnection(settings) as sqlserver:
		cursor = sqlserver.execute("SELECT @@VERSION")

		try:
			row = cursor.fetchone()

			if row is not None:
				logger.info(
					"SQL Server connection successful: %s",
					row[0],
		   	 )
		finally:
			cursor.close()

	try:
		with HyperFileConnection(settings) as hyper:
			repository = HyperFileRepository(hyper)

			for order, lines in repository.iter_orders_with_lines():
				order_count += 1
				line_count += len(lines)

				if not lines:
					orders_without_lines += 1

				if order_count % 1000 == 0:
					elapsed = time.perf_counter() - started_at

					orders_per_second = (
						order_count / elapsed
						if elapsed > 0
						else 0
					)

					logger.info(
						"%d orders and %d lines processed "
						"in %.2f seconds (%.1f orders/second)",
						order_count,
						line_count,
						elapsed,
						orders_per_second,
					)

		elapsed = time.perf_counter() - started_at

		orders_per_second = (
			order_count / elapsed
			if elapsed > 0
			else 0
		)

		logger.info(
			"Completed: %d orders, %d lines, "
			"%d orders without lines in %.2f seconds "
			"(%.1f orders/second)",
			order_count,
			line_count,
			orders_without_lines,
			elapsed,
			orders_per_second,
		)

	except Exception:
		logger.exception("OrderSync failed.")
		raise

if __name__ == "__main__":
	main()