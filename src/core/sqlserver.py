"""
OrderSync

Module:
    sqlserver.py

Description:
    SQL Server connection management.

Author:
    Joan Solé

Version:
    1.0.0
"""

from __future__ import annotations

import pyodbc

from core.settings import Settings
from core.exceptions import SqlServerConnectionError


class SqlServerConnection:
    """
    SQL Server database connection.
    """

    def __init__(self, settings: Settings):

        self._settings = settings
        self._connection = None

    @property
    def connection(self):
        return self._connection

    def connect(self):

        try:

            connection_string = (
                "DRIVER={ODBC Driver 17 for SQL Server};"
                f"SERVER={self._settings.sqlserver.server};"
                f"DATABASE={self._settings.sqlserver.database};"
                "Trusted_Connection=yes;"
            )

            self._connection = pyodbc.connect(connection_string)

        except Exception as ex:

            raise SqlServerConnectionError(str(ex)) from ex

    def disconnect(self):

        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def commit(self):

        if self._connection is not None:
            self._connection.commit()

    def rollback(self):

        if self._connection is not None:
            self._connection.rollback()