"""
OrderSync

Module:
	database_initializer.py

Description:
	Checks and initializes the SQL Server database schema.

Version:
	1.0.0
"""

from pathlib import Path

from core.exceptions import RepositoryError
from core.sqlserver import SqlServerConnection
from core.settings import load_settings
from core.logger import initialise_logger


class DatabaseInitializer:
	"""Initialize the SQL Server schema when required."""

	REQUIRED_TABLES = {
		"COMMANDE",
		"LGCDE",
		"ETL_CONTROL",
		"ETL_RUN",
	}

	def __init__(
		self,
		connection: SqlServerConnection,
		project_root: Path,
	) -> None:
		self._connection = connection
		self._script_path = project_root / "sql" / "table_creation.sql"

	def initialize(self) -> None:
		"""
		Create a brand new database tables if none exists.
		"""
		existing_tables = self._get_existing_tables()
		missing_tables  = self.REQUIRED_TABLES - existing_tables

		if missing_tables:
			if missing_tables != self.REQUIRED_TABLES:
				missing = ", ".join(sorted(missing_tables))
				raise RepositoryError(
					f"Database initialization failed. There are some missing tables: {missing}"
				)
			else:
				self._execute_creation_script()
				logger.info("Database tables created successfully.")
		else:
			logger.info("Database tables already exist.")

		return


	def _get_existing_tables(self) -> set[str]:
		"""Return the existing SQL Server table names."""

		query = """
			SELECT TABLE_NAME
			FROM INFORMATION_SCHEMA.TABLES
			WHERE TABLE_TYPE = 'BASE TABLE'
		"""

		cursor = self._connection.execute(query)

		try:
			return {
				str(row[0]).upper()
				for row in cursor.fetchall()
			}
		finally:
			cursor.close()


	def _execute_creation_script(self) -> None:
		"""Execute table_creation.sql."""

		if not self._script_path.exists():
			raise FileNotFoundError(
				f"SQL creation script not found: {self._script_path}"
			)

		sql_script = self._script_path.read_text(encoding="utf-8")
		cursor = None

		try:
			cursor = self._connection.execute(sql_script)
			self._connection.commit()

		except Exception:
			self._connection.rollback()
			raise

		finally:
			if cursor is not None:
				cursor.close()

if __name__ == "__main__":
	
	
	
	# script location /OrderSync/src/database_initializer.py  target location /OrderSync
	project_root = Path(__file__).resolve().parents[1]

	# final target location /OrderSync/logs
	config_directory = project_root / "config"

	config_directory.mkdir(parents=True, exist_ok=True)
	config_file = config_directory / "config.yaml"

	settings = load_settings(config_file)

	logger = initialise_logger(settings)
	sqlobject=SqlServerConnection(settings)
	sqlobject.connect()

	initializer = DatabaseInitializer(sqlobject, project_root)
	logger.info("Creating database tables...")
	initializer.initialize()
	logger.info("Database tables creation process completed.")



