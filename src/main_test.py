"""
OrderSync

Module:
	main.py
	
Location:
	src\

Description:
	Main entry point for the OrderSync application.

Author:
    Joan Solé
"""

from pathlib import Path

import logging
from core.settings  import load_settings
from core.logger    import initialise_logger
from core.sqlserver import SqlServerConnection
from core.hyperfile import HyperFileConnection
from repositories.hyperfile_repository import HyperFileRepository

import time

def main() -> None:
	
	# script location /OrderSync/src/main.py  target location /OrderSync
	project_root = Path(__file__).resolve().parents[1]

	# final target location /OrderSync/config
	config_directory = project_root / "config"

#	config_directory.mkdir(parents=True, exist_ok=True)
	config_file = config_directory / "config.yaml"

	settings = load_settings(config_file)

	print(settings.application.name)
	print(settings.application.version)
	print(settings.hyperfile.provider)
	print(settings.hyperfile.repository)
	print(settings.sqlserver.server)
	print(settings.sqlserver.database)
	print(settings.application.maj_periode)

	initialise_logger(settings)
	logger = logging.getLogger(__name__)

	logger.info("exemple: Connecting to Hyperfile")
	logger.warning("exemple: This is a warning.")
	logger.error("exemple: This is an error.")
	logger.debug("exemple: Application debug point.")
	logger.exception("exemple: Exception OrderSync failed.")

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
		cursor = sqlserver.execute("SELECT  @@SERVERNAME, DB_NAME(), GETDATE()")
		try:
			row = cursor.fetchone()
			if row is not None:
				logger.info(
					"SQL Server connection successful nom serveur: %s",
					row[0],)
				logger.info(
					"SQL Server connection successful nom DB: %s",
					row[1],)
				logger.info(
					"SQL Server connection successful Date: %s",
					row[2],)				
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