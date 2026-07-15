
"""
OrderSync

Module:
    hyperfile.py

Description:
    HyperFile connection management through OLE DB and ADODB.

Version:
    1.0.0
"""

from __future__ import annotations

from typing import Any

import win32com.client as ole

from .exceptions import HyperFileConnectionError
from .settings   import Settings


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
        Return the active ADODB connection.

        Raises
        ------
        HyperFileConnectionError
            If the connection has not been opened.
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
        config = self._settings.hyperfile

        connection_string = (
            f"Provider={config.provider};"
            f"Initial Catalog={config.repository};"
            f'Extended Properties="Password=*:{config.password}";'
        )

        try:
            self._connection = ole.Dispatch("ADODB.Connection")
            self._connection.Open(connection_string)

        except Exception as exc:
            self._connection = None
            raise HyperFileConnectionError(
                f"Unable to connect to HyperFile: {exc}"
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