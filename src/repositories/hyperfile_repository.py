"""
OrderSync

Module:
    hyperfile_repository.py

Description:
    Reads order headers and order lines from the HyperFile database.

Version:
    1.0.0
"""
from collections import defaultdict
from collections.abc import Iterator
from typing import Any

from core.exceptions import RepositoryError
from core.hyperfile import HyperFileConnection


class HyperFileRepository:
    """Read COMMANDE and LGCDE sequentially from HyperFile."""

    def __init__(self, connection: HyperFileConnection) -> None:
        self._connection = connection

    def iter_orders_with_lines(
        self,
    ) -> Iterator[tuple[dict[str, Any], list[dict[str, Any]]]]:
        """
        Read LGCDE once, group its records by NOCDE, and then read COMMANDE once.

        Yields:
            (order_header, order_lines)
        """

        lines_by_order = self._load_lines_by_order()

        for order in self.iter_orders():
            nocde = order["NOCDE"]

            # pop() returns the lines and removes them from the dictionary.
            # This progressively releases memory.
            lines = lines_by_order.pop(nocde, [])

            yield order, lines

    def iter_orders(self) -> Iterator[dict[str, Any]]:
        """Read every COMMANDE record sequentially using one query."""

        query = """
            SELECT
                TYPCDE,
                NOCDE,
                CFOUR,
                CCOMPTE,
                LIBCDE,
                DTCDE,
                HEURECDE
            FROM COMMANDE
            ORDER BY NOCDE
        """

        recordset = None

        try:
            recordset = self._execute(query)

            while not recordset.EOF:
                yield self._build_order(recordset)
                recordset.MoveNext()

        except Exception as exc:
            raise RepositoryError(
                f"Unable to read COMMANDE sequentially: {exc}"
            ) from exc

        finally:
            self._close_recordset(recordset)

    def iter_order_lines(self) -> Iterator[dict[str, Any]]:
        """Read every LGCDE record sequentially using one query."""

        query = """
            SELECT
                NOCDE,
                CMARQ,
                CLIGNE,
                CCATEG,
                CPROD,
                PAAR,
                PAMP,
                QTESTK,
                QTECDE,
                QTERECU,
                MTLIG
            FROM LGCDE
            ORDER BY NOCDE, CMARQ, CCATEG, CPROD
        """

        recordset = None

        try:
            recordset = self._execute(query)

            while not recordset.EOF:
                yield self._build_line(recordset)
                recordset.MoveNext()

        except Exception as exc:
            raise RepositoryError(
                f"Unable to read LGCDE sequentially: {exc}"
            ) from exc

        finally:
            self._close_recordset(recordset)

    def _load_lines_by_order(
        self,
    ) -> dict[str, list[dict[str, Any]]]:
        """
        Build an in-memory lookup:

            NOCDE -> list of LGCDE records
        """

        lines_by_order: defaultdict[
            str,
            list[dict[str, Any]],
        ] = defaultdict(list)

        for line in self.iter_order_lines():
            nocde = line["NOCDE"]
            lines_by_order[nocde].append(line)

        return dict(lines_by_order)

    def _build_order(self, recordset: Any) -> dict[str, Any]:
        return {
            "TYPCDE": self._text_value(recordset, "TYPCDE"),
            "NOCDE": self._text_value(recordset, "NOCDE"),
            "CFOUR": self._text_value(recordset, "CFOUR"),
            "CCOMPTE": self._text_value(recordset, "CCOMPTE"),
            "LIBCDE": self._text_value(recordset, "LIBCDE"),
            "DTCDE": self._field_value(recordset, "DTCDE", None),
            "HEURECDE": self._text_value(recordset, "HEURECDE"),
        }

    def _build_line(self, recordset: Any) -> dict[str, Any]:
        return {
            "NOCDE": self._text_value(recordset, "NOCDE"),
            "CMARQ": self._text_value(recordset, "CMARQ"),
            "CLIGNE": self._integer_value(recordset, "CLIGNE"),
            "CCATEG": self._text_value(recordset, "CCATEG"),
            "CPROD": self._text_value(recordset, "CPROD"),
            "PAAR": self._float_value(recordset, "PAAR"),
            "PAMP": self._float_value(recordset, "PAMP"),
            "QTESTK": self._float_value(recordset, "QTESTK"),
            "QTECDE": self._float_value(recordset, "QTECDE"),
            "QTERECU": self._float_value(recordset, "QTERECU"),
            "MTLIG": self._float_value(recordset, "MTLIG"),
        }

    def _execute(self, query: str) -> Any:
        return self._connection.execute(query)

    @staticmethod
    def _field_value(
        recordset: Any,
        field_name: str,
        default: Any = None,
    ) -> Any:
        value = recordset.Fields(field_name).Value

        if value is None:
            return default

        return value

    def _text_value(
        self,
        recordset: Any,
        field_name: str,
        default: str = "",
    ) -> str:
        value = self._field_value(recordset, field_name, default)
        return str(value).strip()

    def _integer_value(
        self,
        recordset: Any,
        field_name: str,
        default: int = 0,
    ) -> int:
        value = self._field_value(recordset, field_name, default)

        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def _float_value(
        self,
        recordset: Any,
        field_name: str,
        default: float = 0.0,
    ) -> float:
        value = self._field_value(recordset, field_name, default)

        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _close_recordset(recordset: Any) -> None:
        if recordset is None:
            return

        try:
            if recordset.State != 0:
                recordset.Close()
        except Exception:
            pass