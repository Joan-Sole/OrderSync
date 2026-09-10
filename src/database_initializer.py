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
        Create the database tables when one or more are missing.
        """
        existing_tables = self._get_existing_tables()
        missing_tables = self.REQUIRED_TABLES - existing_tables

        if not missing_tables:
            return

        self._execute_creation_script()

        existing_tables = self._get_existing_tables()
        missing_tables = self.REQUIRED_TABLES - existing_tables

        if missing_tables:
            missing = ", ".join(sorted(missing_tables))

            raise RepositoryError(
                f"Database initialization failed. Missing tables: {missing}"
            )

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

        try:
            cursor = self._connection.execute(sql_script)
            cursor.close()
            self._connection.commit()

        except Exception:
            self._connection.rollback()
            raise