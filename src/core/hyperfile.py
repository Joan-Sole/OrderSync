
"""
OrderSync

Module:
    hyperfile.py
    
Location:
    src\\core

Description:
    HyperFile connection management through OLE DB and ADODB.

Version:
    1.0.0
"""

from typing import Any

import win32com.client as ole

from .exceptions import HyperFileConnectionError
from .settings import Settings
import logging

logger = logging.getLogger(__name__)

class HyperFileConnection:
    """
    Manage an ADODB connection to a HyperFile database.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._connection: Any | None = None

    @property
    def connection(self) -> Any:
        """
        Return the active native ADODB connection.

        This property should normally only be used for exceptional cases.
        Repository classes should preferably call execute().
        """
        if self._connection is None:
            raise HyperFileConnectionError(
                "HyperFile connection is not open."
            )

        return self._connection

    def connect(self) -> None:
        """
        Open the HyperFile OLE DB connection.
        """
        if self._connection is not None:
            return

        config = self._settings.hyperfile

        connection_string = (
            f"Provider={config.provider};"
            f"Initial Catalog={config.repository};"
            f'Extended Properties="Password=*:{config.password}";'
        )

        try:
            connection = ole.Dispatch("ADODB.Connection")
            connection.Open(connection_string)

            self._connection = connection

        except Exception as exc:
            self._connection = None

            raise HyperFileConnectionError(
                f"Unable to connect to HyperFile: {exc}"
            ) from exc

    def execute(self, query: str) -> Any:
        """
        Execute a query through the active ADODB connection.

        Parameters
        ----------
        query:
            SQL statement to execute.

        Returns
        -------
        Any
            The ADODB Recordset returned by Execute().
        """
        try:
            result = self.connection.Execute(query)

            # Depending on the pywin32/COM interface, Execute may return
            # either the Recordset directly or a tuple containing it.
            if isinstance(result, tuple):
                return result[0]

            return result

        except Exception as exc:
            raise HyperFileConnectionError(
                f"Unable to execute HyperFile query: {exc}"
            ) from exc

    def disconnect(self) -> None:
        """
        Close the HyperFile connection.
        """
        if self._connection is None:
            return

        try:
            if self._connection.State != 0:
                self._connection.Close()

        except Exception as exc:
            raise HyperFileConnectionError(
                f"Unable to disconnect from HyperFile: {exc}"
            ) from exc

        finally:
            self._connection = None

    def __enter__(self) -> "HyperFileConnection":
        self.connect()
        return self

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception_value: BaseException | None,
        traceback: Any | None,
    ) -> None:
        self.disconnect()