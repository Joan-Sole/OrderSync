"""
OrderSync

Module:
    hyperfile_repository.py

Location:
    src\\repositories

Description:
    Reads order headers and order lines from the HyperFile database.

Version:
    1.0.0
"""
from collections import defaultdict
from collections.abc import Iterator
from typing import Any
from pathlib import Path

from core.exceptions import RepositoryError, ValidationError
from core.hyperfile import HyperFileConnection
from core.settings import load_settings

from models.commande import Commande
from models.lgcde import Lgcde
import logging

from datetime import date, datetime, timedelta

logger = logging.getLogger(__name__)

class HyperFileRepository:
    """Read COMMANDE and LGCDE sequentially from HyperFile."""

    def __init__(self, connection: HyperFileConnection) -> None:
        self._connection = connection


    def filter_orders_by_date_clause(self, per: Any | None = None, where: str ='', field: str ='DTCDE') -> str:
        """
        Return a SQL WHERE clause to filter orders by date.

        Args:
            per (int): Number of weeks to look back from today. By default is loaded as settings.application.maj_periode
            where (str): Can insert and existing SQL WHERE clause to append to. We assume no blanks at the beginning
            field (str): Date field used for filtering.

        Returns:
            str: SQL WHERE clause.
        """

        if per is None:
            
            # script location /OrderSync/src/repositories/hyperfile_repository.py  target location /OrderSync
            project_root = Path(__file__).resolve().parents[2]

            # final target location /OrderSync/config
            config_directory = project_root / "config"

            config_file = config_directory / "config.yaml"
            settings = load_settings(config_file)
            per = settings.application.maj_periode

        try:
            periode=int(per)
        except (TypeError, ValueError):
            periode = 0

        if periode <= 0:
            logger.warning("Période de filtrage désactivée.")
            return where

        filter_date = date.today() - timedelta(weeks=periode)

        condition = (
            f"{field} >= '{filter_date.strftime('%Y%m%d')}'"
        )

        if where:
            return f"{where} AND {condition}"

        return f"WHERE {condition}"

    
    def iter_orders_with_lines(
        self,
    ) -> Iterator[tuple[Commande, list[Lgcde]]]:
        """
        Read LGCDE once, group its records by NOCDE,
        and then read COMMANDE once.

        Yields:
            (Commande, list[Lgcde])
        """

        lines_by_order = self._load_lines_by_order()

        for order in self.iter_orders():
            nocde = order.NOCDE

            # Return the lines and remove them from the dictionary
            # to progressively release memory.            
#            if nocde not in lines_by_order:
#                lines_by_order[nocde] = []


            lines = lines_by_order.pop(nocde, [])

            yield order, lines



    def iter_orders(self) -> Iterator[Commande]:
        """Read every COMMANDE record sequentially using one query."""

        where_clause = self.filter_orders_by_date_clause()

        query = f"""
            SELECT
                TYPCDE,
                NOCDE,
                CFOUR,
                CCOMPTE,
                LIBCDE,
                DTCDE,
                HEURECDE,
                NOCHRONO,
                OBSER,
                MODECDE,
                DTLIVPREVU,
                NBJOURS,
                CDECENTRAL,
                TXREM,
                MTCDE,
                MTRECU,
                MAGCDE,
                MAGLIVR,
                RETOUR_CDE,
                DTREC,
                DTFACT,
                FORMAT_EDI,
                STATUTEDI
                
            FROM COMMANDE 
            {where_clause}
            ORDER BY NOCDE
        """

        recordset = None

        try:
            recordset = self._execute(query)

            while not recordset.EOF:
                try:
                    order = self._build_order(recordset)
                    yield order
                except ValidationError as exc:
                    logger.warning(
                        "COMMANDE discarded: %s",
                        exc,
                    )
                finally:
                    recordset.MoveNext()

        except Exception as exc:
            raise RepositoryError(
                f"Unable to read COMMANDE sequentially: {exc}"
            ) from exc

        finally:
            self._close_recordset(recordset)


    def iter_order_lines(self) -> Iterator[Lgcde]:
        """Read every LGCDE record sequentially using one query."""

        where_clause = self.filter_orders_by_date_clause(field="COMMANDE.DTCDE")
        
        query = f"""
        SELECT
            LGCDE.TYPCDE,
            LGCDE.NOCDE,
            LGCDE.CMARQ,
            LGCDE.CCATEG,
            LGCDE.CPROD,
            LGCDE.PAAR,
            LGCDE.PAMP,
            LGCDE.QTESTK,
            LGCDE.QTECDE,
            LGCDE.TXREM,
            LGCDE.TVA,
            LGCDE.QTERECU,
            LGCDE.QTEREFUS,
            LGCDE.QTEFAC,
            LGCDE.MTLIG
        FROM LGCDE
        INNER JOIN COMMANDE
            ON LGCDE.NOCDE = COMMANDE.NOCDE
            {where_clause}
        ORDER BY
            LGCDE.NOCDE,
            LGCDE.CMARQ,
            LGCDE.CCATEG,
            LGCDE.CPROD
        """

        recordset = None

        try:
            recordset = self._execute(query)

            while not recordset.EOF:
                try:
                    line = self._build_line(recordset)
                    yield line
                except ValidationError as exc:
                    logger.warning(
                        "LGCDE discarded: %s",
                        exc,
                    )
                finally:
                    recordset.MoveNext()

        except Exception as exc:
            raise RepositoryError(
                f"Unable to read LGCDE sequentially: {exc}"
            ) from exc

        finally:
            self._close_recordset(recordset)


    def _load_lines_by_order(
        self,
    ) -> dict[str, list[Lgcde]]:
        """
        Build an in-memory lookup:

            NOCDE -> list of LGCDE records
        """

        lines_by_order: defaultdict[
            str,
            list[Lgcde],
        ] = defaultdict(list)

        for line in self.iter_order_lines():
            nocde = line.NOCDE
            lines_by_order[nocde].append(line)

        return dict(lines_by_order)


    def _build_order(self, recordset: Any) -> Commande:
        return Commande (
            TYPCDE=self._required_text_value(recordset, "TYPCDE"),
            NOCDE=self._required_text_value(recordset, "NOCDE"),
            CFOUR=self._required_text_value(recordset, "CFOUR"),
            CCOMPTE=self._text_value(recordset, "CCOMPTE"),
            LIBCDE=self._text_value(recordset, "LIBCDE"),
            DTCDE=self._required_date_value(recordset, "DTCDE"),
            HEURECDE=self._text_value(recordset, "HEURECDE"),
            NOCHRONO=self._text_value(recordset, "NOCHRONO"),
            OBSER=self._text_value(recordset, "OBSER"),
            MODECDE=self._text_value(recordset, "MODECDE"),
            DTLIVPREVU=self._date_value(recordset, "DTLIVPREVU"),
            NBJOURS=self._text_value(recordset, "NBJOURS"),
            CDECENTRAL=self._boolean_value(recordset, "CDECENTRAL"),
            TXREM=self._float_value(recordset, "TXREM"),
            MTCDE=self._float_value(recordset, "MTCDE"),
            MTRECU=self._float_value(recordset, "MTRECU"),
            MAGCDE=self._text_value(recordset, "MAGCDE"),
            MAGLIVR=self._text_value(recordset, "MAGLIVR"),
            RETOUR_CDE=self._text_value(recordset, "RETOUR_CDE"),
            DTREC=self._date_value(recordset, "DTREC"),
            DTFACT=self._date_value(recordset, "DTFACT"),
            FORMAT_EDI=self._boolean_value(recordset, "FORMAT_EDI"),
            STATUTEDI=self._text_value(recordset, "STATUTEDI"),
        )

    def _build_line(self, recordset: Any) -> Lgcde:
        return Lgcde(
            TYPCDE=self._required_text_value(recordset, "TYPCDE"),
            NOCDE=self._required_text_value(recordset, "NOCDE"),
            CMARQ=self._required_text_value(recordset, "CMARQ"),
            CCATEG=self._required_text_value(recordset, "CCATEG"),
            CPROD=self._required_text_value(recordset, "CPROD"),
            PAAR=self._float_value(recordset, "PAAR"),
            PAMP=self._float_value(recordset, "PAMP"),
            QTESTK=self._integer_value(recordset, "QTESTK"),
            QTECDE=self._integer_value(recordset, "QTECDE"),
            TXREM=self._float_value(recordset, "TXREM"),
            TVA=self._float_value(recordset, "TVA"),
            QTERECU=self._integer_value(recordset, "QTERECU"),
            QTEREFUS=self._integer_value(recordset, "QTEREFUS"),
            QTEFAC=self._integer_value(recordset, "QTEFAC"),
            MTLIG=self._float_value(recordset, "MTLIG"),
        )

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
 ) -> str | None:
        value = self._field_value(recordset, field_name, default)

        if value is None:
            return None

        return str(value).strip()


    def _required_text_value(
        self,
        recordset: Any,
        field_name: str,
    ) -> str:
        value = self._field_value(recordset, field_name, None)

        if value is None:
            raise ValidationError(
                f"Required field {field_name} is NULL."
            )

        value = str(value).strip()

        if not value:
            raise ValidationError(
                f"Required field {field_name} is empty."
            )

        return value


    def _integer_value(
        self,
        recordset: Any,
        field_name: str,
    ) -> int | None:
        
        value = self._field_value(recordset, field_name, None)

        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None


    def _float_value(
        self,
        recordset: Any,
        field_name: str,
    ) -> float | None:

        value = self._field_value(recordset, field_name, None)

        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None


    def _boolean_value(
        self,
        recordset: Any,
        field_name: str,
    ) -> bool | None:
        value = self._field_value(recordset, field_name, None)

        if value is None:
            return None
        try:
            return bool(int(value))
        except (ValueError, TypeError):
            return None


    def _date_value(
        self,
        recordset: Any,
        field_name: str,
    ) -> date | None:

        value = self._field_value(recordset, field_name, None)

        if value is None:
            return None

        if isinstance(value, datetime):
            return value.date()

        if isinstance(value, date):
            return value

        return None


    def _required_date_value(
        self,
        recordset: Any,
        field_name: str,
    ) -> date:
        value = self._date_value(recordset, field_name)

        if value is None:
            raise ValidationError(
                f"Required date field {field_name} is NULL or invalid."
            )

        return value


    @staticmethod
    def _close_recordset(recordset: Any) -> None:
        if recordset is None:
            return

        try:
            if recordset.State != 0:
                recordset.Close()
        except Exception:
            pass