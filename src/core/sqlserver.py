"""
OrderSync

Module:
    sqlserver.py

Description:
    SQL Server connection management through pyodbc.

Version:
    1.0.0
"""

from __future__ import annotations

from typing import Any

import pyodbc

from .exceptions import SqlServerConnectionError
from .settings import Settings


class SqlServerConnection:
    """
    Manage a pyodbc connection to a SQL Server database.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._connection: pyodbc.Connection | None = None

    @property
    def connection(self) -> pyodbc.Connection:
        """
        Return the active SQL Server connection.

        Raises
        ------
        SqlServerConnectionError
            If the connection has not been opened.
        """
        if self._connection is None:
            raise SqlServerConnectionError(
                "SQL Server connection is not open."
            )

        return self._connection

    def connect(self) -> None:
        """
        Open the SQL Server connection.
        """
        if self._connection is not None:
            return

        config = self._settings.sqlserver

        connection_string = self._build_connection_string()

        try:
            self._connection = pyodbc.connect(
                connection_string,
                autocommit=False,
                timeout=config.timeout,
            )

        except pyodbc.Error as exc:
            self._connection = None

            raise SqlServerConnectionError(
                f"Unable to connect to SQL Server: {exc}"
            ) from exc

    def _build_connection_string(self) -> str:
        """
        Build the pyodbc SQL Server connection string.
        """
        config = self._settings.sqlserver

        parts = [
            f"DRIVER={{{config.driver}}}",
            f"SERVER={config.server}",
            f"DATABASE={config.database}",
            "TrustServerCertificate=yes",
        ]

        if config.trusted_connection:
            parts.append("Trusted_Connection=yes")
        else:
            parts.extend(
                [
                    f"UID={config.username}",
                    f"PWD={config.password}",
                ]
            )

        return ";".join(parts) + ";"

    def cursor(self) -> pyodbc.Cursor:
        """
        Create and return a cursor from the active connection.
        """
        try:
            return self.connection.cursor()

        except SqlServerConnectionError:
            raise

        except pyodbc.Error as exc:
            raise SqlServerConnectionError(
                f"Unable to create SQL Server cursor: {exc}"
            ) from exc

    def execute(
        self,
        query: str,
        parameters: tuple[Any, ...] | None = None,
    ) -> pyodbc.Cursor:
        """
        Execute a SQL statement.

        Parameters
        ----------
        query:
            SQL statement to execute.

        parameters:
            Optional parameters used by the SQL statement.

        Returns
        -------
        pyodbc.Cursor
            Cursor containing the execution result.
        """
        cursor = self.cursor()

        try:
            if parameters is None:
                cursor.execute(query)
            else:
                cursor.execute(query, parameters)

            return cursor

        except pyodbc.Error as exc:
            cursor.close()

            raise SqlServerConnectionError(
                f"Unable to execute SQL Server query: {exc}"
            ) from exc

    def executemany(
        self,
        query: str,
        parameters: list[tuple[Any, ...]],
        *,
        fast: bool = True,
    ) -> pyodbc.Cursor:
        """
        Execute the same SQL statement for multiple parameter sets.

        Parameters
        ----------
        query:
            Parameterized SQL statement to execute.

        parameters:
            Collection of parameter tuples.

        fast:
            Enable pyodbc fast_executemany.

        Returns
        -------
        pyodbc.Cursor
            Cursor used for the operation.
        """
        cursor = self.cursor()

        try:
            cursor.fast_executemany = fast
            cursor.executemany(query, parameters)

            return cursor

        except pyodbc.Error as exc:
            cursor.close()

            raise SqlServerConnectionError(
                f"Unable to execute SQL Server batch: {exc}"
            ) from exc

    def commit(self) -> None:
        """
        Commit the current SQL Server transaction.
        """
        try:
            self.connection.commit()

        except SqlServerConnectionError:
            raise

        except pyodbc.Error as exc:
            raise SqlServerConnectionError(
                f"Unable to commit SQL Server transaction: {exc}"
            ) from exc

    def rollback(self) -> None:
        """
        Roll back the current SQL Server transaction.
        """
        try:
            self.connection.rollback()

        except SqlServerConnectionError:
            raise

        except pyodbc.Error as exc:
            raise SqlServerConnectionError(
                f"Unable to roll back SQL Server transaction: {exc}"
            ) from exc

    def disconnect(self) -> None:
        """
        Close the SQL Server connection.
        """
        if self._connection is None:
            return

        try:
            self._connection.close()

        except pyodbc.Error as exc:
            raise SqlServerConnectionError(
                f"Unable to disconnect from SQL Server: {exc}"
            ) from exc

        finally:
            self._connection = None

    def __enter__(self) -> "SqlServerConnection":
        self.connect()
        return self

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception_value: BaseException | None,
        traceback: Any | None,
    ) -> None:
        if exception_type is not None:
            try:
                self.rollback()
            finally:
                self.disconnect()
        else:
            self.disconnect()