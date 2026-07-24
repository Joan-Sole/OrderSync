"""
OrderSync

Module:
    sqlserver_repository.py

Description:
    Repository for accessing OrderSync data stored in SQL Server.

Version:
    1.0.0
"""

from __future__ import annotations

from typing import Any

from core.sqlserver import SqlServerConnection


class SqlServerRepository:
    """
    Provide access to OrderSync tables stored in SQL Server.
    """

    def __init__(
        self,
        connection: SqlServerConnection,
    ) -> None:
        self._connection = connection

    def count_orders(self) -> int:
        """
        Return the total number of order headers stored in SQL Server.
        """
        query = """
            SELECT COUNT(*)
            FROM orders_header
        """

        cursor = self._connection.execute(query)

        try:
            row = cursor.fetchone()

            if row is None:
                return 0

            return int(row[0])

        finally:
            cursor.close()

    def count_order_lines(self) -> int:
        """
        Return the total number of order lines stored in SQL Server.
        """
        query = """
            SELECT COUNT(*)
            FROM orders_lines
        """

        cursor = self._connection.execute(query)

        try:
            row = cursor.fetchone()

            if row is None:
                return 0

            return int(row[0])

        finally:
            cursor.close()

    def order_exists(self, order_number: str) -> bool:
        """
        Check whether an order already exists in SQL Server.

        Parameters
        ----------
        order_number:
            HyperFile order number.

        Returns
        -------
        bool
            True when the order exists.
        """
        query = """
            SELECT 1
            FROM orders_header
            WHERE order_number = ?
        """

        cursor = self._connection.execute(
            query,
            (order_number,),
        )

        try:
            return cursor.fetchone() is not None

        finally:
            cursor.close()

    def get_order_status(
        self,
        order_number: str,
    ) -> int | None:
        """
        Return the current status of an order.

        Parameters
        ----------
        order_number:
            HyperFile order number.

        Returns
        -------
        int | None
            Order status, or None when the order does not exist.
        """
        query = """
            SELECT status
            FROM orders_header
            WHERE order_number = ?
        """

        cursor = self._connection.execute(
            query,
            (order_number,),
        )

        try:
            row = cursor.fetchone()

            if row is None:
                return None

            return int(row[0])

        finally:
            cursor.close()

    def get_order_line_count(
        self,
        order_number: str,
    ) -> int:
        """
        Return the number of lines stored for an order.
        """
        query = """
            SELECT COUNT(*)
            FROM orders_lines
            WHERE order_number = ?
        """

        cursor = self._connection.execute(
            query,
            (order_number,),
        )

        try:
            row = cursor.fetchone()

            if row is None:
                return 0

            return int(row[0])

        finally:
            cursor.close()

    def get_database_information(self) -> dict[str, Any]:
        """
        Return basic information about the SQL Server connection.
        """
        query = """
            SELECT
                @@SERVERNAME AS server_name,
                DB_NAME() AS database_name,
                GETDATE() AS server_datetime
        """

        cursor = self._connection.execute(query)

        try:
            row = cursor.fetchone()

            if row is None:
                return {}

            return {
                "server_name": row[0],
                "database_name": row[1],
                "server_datetime": row[2],
            }

        finally:
            cursor.close()