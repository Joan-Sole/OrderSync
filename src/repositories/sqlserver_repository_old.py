"""
OrderSync

Module:
    sqlserver_repository.py
    
Location:
    src\\repositories

Description:
    Repository for accessing COMMANDE and LGCDE data stored in SQL Server.
    SQL Server table and field names preserve the original HyperFile names.

Author:
    Joan Solé
"""

from __future__ import annotations

from typing import Any
import logging
from core.sqlserver import SqlServerConnection
from models.commande import Commande
from models.lgcde import Lgcde

logger = logging.getLogger(__name__)

class SqlServerRepository:
    """Provide access to COMMANDE and LGCDE stored in SQL Server."""

    def __init__(self, connection: SqlServerConnection) -> None:
        self._connection = connection

    def get_database_information(self) -> dict[str, Any]:
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

    def count_commandes(self) -> int:
        cursor = self._connection.execute(
            "SELECT COUNT(*) FROM COMMANDE"
        )

        try:
            row = cursor.fetchone()
            return 0 if row is None else int(row[0])

        finally:
            cursor.close()

    def commande_exists(self, nocde: str) -> bool:
        query = """
            SELECT 1
            FROM COMMANDE
            WHERE NOCDE = ?
        """

        cursor = self._connection.execute(query, (nocde,))

        try:
            return cursor.fetchone() is not None

        finally:
            cursor.close()

    def get_commande_status(self, nocde: str) -> str | None:
        query = """
            SELECT TYPCDE
            FROM COMMANDE
            WHERE NOCDE = ?
        """

        cursor = self._connection.execute(query, (nocde,))

        try:
            row = cursor.fetchone()

            if row is None or row[0] is None:
                return None

            return str(row[0]).strip()

        finally:
            cursor.close()

    def insert_commande(self, commande: Commande) -> None:
        query = """
            INSERT INTO COMMANDE (
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
            )
            VALUES (
                ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?
            )
        """

        parameters = (
            commande.TYPCDE,
            commande.NOCDE,
            commande.CFOUR,
            commande.CCOMPTE,
            commande.LIBCDE,
            commande.DTCDE,
            commande.HEURECDE,
            commande.NOCHRONO,
            commande.OBSER,
            commande.MODECDE,
            commande.DTLIVPREVU,
            commande.NBJOURS,
            None if commande.CDECENTRAL is None else int(commande.CDECENTRAL),
            commande.TXREM,
            commande.MTCDE,
            commande.MTRECU,
            commande.MAGCDE,
            commande.MAGLIVR,
            commande.RETOUR_CDE,
            commande.DTREC,
            commande.DTFACT,
            None if commande.FORMAT_EDI is None else int(commande.FORMAT_EDI),     
            commande.STATUTEDI,
        )

        cursor = self._connection.execute(query, parameters)
        cursor.close()

    def count_lgcde(self) -> int:
        cursor = self._connection.execute(
            "SELECT COUNT(*) FROM LGCDE"
        )

        try:
            row = cursor.fetchone()
            return 0 if row is None else int(row[0])

        finally:
            cursor.close()

    def count_lgcde_for_commande(self, nocde: str) -> int:
        query = """
            SELECT COUNT(*)
            FROM LGCDE
            WHERE NOCDE = ?
        """

        cursor = self._connection.execute(query, (nocde,))

        try:
            row = cursor.fetchone()
            return 0 if row is None else int(row[0])

        finally:
            cursor.close()

    def lgcde_exists(
        self,
        nocde: str,
        cmarq: str,
        ccateg: str,
        cprod: str,
    ) -> bool:
        query = """
            SELECT 1
            FROM LGCDE
            WHERE
                NOCDE = ?
                AND CMARQ = ?
                AND CCATEG = ?
                AND CPROD = ?
        """

        cursor = self._connection.execute(
            query,
            (
                nocde,
                cmarq,
                ccateg,
                cprod,
            ),
        )

        try:
            return cursor.fetchone() is not None

        finally:
            cursor.close()

    def insert_lgcde(self, line: Lgcde) -> None:
        query = """
            INSERT INTO LGCDE (
                TYPCDE,
                NOCDE,
                CMARQ,
                CCATEG,
                CPROD,
                PAAR,
                PAMP,
                QTESTK,
                QTECDE,
                TXREM,
	            TVA,
                QTERECU,
                QTEREFUS,
                QTEFAC,
                MTLIG
            )
            VALUES (
                ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, 
                ?, ?, ?
            )
        """

        parameters = (
            line.TYPCDE,
            line.NOCDE,
            line.CMARQ,
            line.CCATEG,
            line.CPROD,
            line.PAAR,
            line.PAMP,
            line.QTESTK,
            line.QTECDE,
            line.TXREM,
            line.TVA,
            line.QTERECU,
            line.QTEREFUS,
            line.QTEFAC,
            line.MTLIG,
        )

        cursor = self._connection.execute(query, parameters)
        cursor.close()
