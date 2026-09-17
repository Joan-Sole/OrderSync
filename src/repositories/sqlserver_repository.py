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


    # ============================================================
    # Database information
    # ============================================================

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


    # ============================================================
    # COMMANDE
    # ============================================================

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


    def get_commande(
        self,
        nocde: str,
    ) -> Commande | None:
        """
        Return one COMMANDE from SQL Server.

        Returns None if NOCDE does not exist.
        """

        query = """
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
            WHERE NOCDE = ?
        """

        cursor = self._connection.execute(
            query,
            (nocde,),
        )

        try:
            row = cursor.fetchone()

            if row is None:
                return None

            return self._build_commande(row)

        finally:
            cursor.close()


    def get_commande_status(
        self,
        nocde: str,
    ) -> str | None:

        query = """
            SELECT TYPCDE
            FROM COMMANDE
            WHERE NOCDE = ?
        """

        cursor = self._connection.execute(
            query,
            (nocde,),
        )

        try:
            row = cursor.fetchone()

            if row is None or row[0] is None:
                return None

            return str(row[0]).strip()

        finally:
            cursor.close()


    def insert_commande(
        self,
        commande: Commande,
    ) -> None:

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

        parameters = self._commande_parameters(
            commande
        )

        cursor = self._connection.execute(
            query,
            parameters,
        )

        cursor.close()


    def update_commande(
        self,
        commande: Commande,
    ) -> None:

        query = """
            UPDATE COMMANDE
            SET
                TYPCDE = ?,
                CFOUR = ?,
                CCOMPTE = ?,
                LIBCDE = ?,
                DTCDE = ?,
                HEURECDE = ?,
                NOCHRONO = ?,
                OBSER = ?,
                MODECDE = ?,
                DTLIVPREVU = ?,
                NBJOURS = ?,
                CDECENTRAL = ?,
                TXREM = ?,
                MTCDE = ?,
                MTRECU = ?,
                MAGCDE = ?,
                MAGLIVR = ?,
                RETOUR_CDE = ?,
                DTREC = ?,
                DTFACT = ?,
                FORMAT_EDI = ?,
                STATUTEDI = ?
            WHERE NOCDE = ?
        """

        parameters = (
            commande.TYPCDE,
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
            None if commande.CDECENTRAL is None
            else int(commande.CDECENTRAL),
            commande.TXREM,
            commande.MTCDE,
            commande.MTRECU,
            commande.MAGCDE,
            commande.MAGLIVR,
            commande.RETOUR_CDE,
            commande.DTREC,
            commande.DTFACT,
            None if commande.FORMAT_EDI is None
            else int(commande.FORMAT_EDI),
            commande.STATUTEDI,
            commande.NOCDE,
        )

        cursor = self._connection.execute(
            query,
            parameters,
        )

        cursor.close()


    def get_commandes_for_reconciliation(
        self,
    ) -> list[Commande]:
        """
        Return all COMMANDE records required for the final
        synchronization reconciliation.
        """

        query = """
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
        """

        cursor = self._connection.execute(query)

        try:
            result: list[Commande] = []

            for row in cursor.fetchall():
                result.append(
                    self._build_commande(row)
                )

            return result

        finally:
            cursor.close()


    def finalize_commande(
        self,
        nocde: str,
    ) -> None:
        """
        Mark a COMMANDE as finalized.
        """

        query = """
            UPDATE COMMANDE
            SET TYPCDE = 'V'
            WHERE NOCDE = ?
        """

        cursor = self._connection.execute(
            query,
            (nocde,),
        )

        cursor.close()


    def delete_commande(
        self,
        nocde: str,
    ) -> None:
        """
        Delete one COMMANDE and all its LGCDE records.

        LGCDE must be deleted first because it references COMMANDE.
        """

        cursor = self._connection.execute(
            """
            DELETE FROM LGCDE
            WHERE NOCDE = ?
            """,
            (nocde,),
        )

        cursor.close()

        cursor = self._connection.execute(
            """
            DELETE FROM COMMANDE
            WHERE NOCDE = ?
            """,
            (nocde,),
        )

        cursor.close()


    # ============================================================
    # LGCDE
    # ============================================================

    def count_lgcde(self) -> int:

        cursor = self._connection.execute(
            "SELECT COUNT(*) FROM LGCDE"
        )

        try:
            row = cursor.fetchone()
            return 0 if row is None else int(row[0])

        finally:
            cursor.close()


    def count_lgcde_for_commande(
        self,
        nocde: str,
    ) -> int:

        query = """
            SELECT COUNT(*)
            FROM LGCDE
            WHERE NOCDE = ?
        """

        cursor = self._connection.execute(
            query,
            (nocde,),
        )

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


    def get_lgcde_for_commande(
        self,
        nocde: str,
    ) -> dict[
        tuple[str, str, str, str],
        Lgcde,
    ]:
        """
        Return all LGCDE records belonging to one COMMANDE.

        Dictionary key:
            (NOCDE, CMARQ, CCATEG, CPROD)
        """

        query = """
            SELECT
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
            FROM LGCDE
            WHERE NOCDE = ?
        """

        cursor = self._connection.execute(
            query,
            (nocde,),
        )

        try:
            result: dict[
                tuple[str, str, str, str],
                Lgcde,
            ] = {}

            for row in cursor.fetchall():

                line = self._build_lgcde(row)

                result[line.line_key] = line

            return result

        finally:
            cursor.close()


    def insert_lgcde(
        self,
        line: Lgcde,
    ) -> None:

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

        cursor = self._connection.execute(
            query,
            parameters,
        )

        cursor.close()


    def update_lgcde(
        self,
        line: Lgcde,
    ) -> None:

        query = """
            UPDATE LGCDE
            SET
                TYPCDE = ?,
                PAAR = ?,
                PAMP = ?,
                QTESTK = ?,
                QTECDE = ?,
                TXREM = ?,
                TVA = ?,
                QTERECU = ?,
                QTEREFUS = ?,
                QTEFAC = ?,
                MTLIG = ?
            WHERE
                NOCDE = ?
                AND CMARQ = ?
                AND CCATEG = ?
                AND CPROD = ?
        """

        parameters = (
            line.TYPCDE,
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
            line.NOCDE,
            line.CMARQ,
            line.CCATEG,
            line.CPROD,
        )

        cursor = self._connection.execute(
            query,
            parameters,
        )

        cursor.close()


    def delete_lgcde(
        self,
        line_key: tuple[str, str, str, str],
    ) -> None:

        nocde, cmarq, ccateg, cprod = line_key

        query = """
            DELETE FROM LGCDE
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

        cursor.close()


    # ============================================================
    # Internal builders
    # ============================================================

    @staticmethod
    def _build_commande(row: Any) -> Commande:
        """
        Build a Commande model from one SQL Server row.
        """

        return Commande(
            TYPCDE=str(row[0]).strip(),
            NOCDE=str(row[1]).strip(),
            CFOUR=str(row[2]).strip(),
            CCOMPTE=None if row[3] is None else str(row[3]).strip(),
            LIBCDE=None if row[4] is None else str(row[4]).strip(),
            DTCDE=row[5],
            HEURECDE=None if row[6] is None else str(row[6]).strip(),
            NOCHRONO=None if row[7] is None else str(row[7]).strip(),
            OBSER=None if row[8] is None else str(row[8]).strip(),
            MODECDE=None if row[9] is None else str(row[9]).strip(),
            DTLIVPREVU=row[10],
            NBJOURS=None if row[11] is None else str(row[11]).strip(),
            CDECENTRAL=None if row[12] is None else bool(row[12]),
            TXREM=None if row[13] is None else float(row[13]),
            MTCDE=None if row[14] is None else float(row[14]),
            MTRECU=None if row[15] is None else float(row[15]),
            MAGCDE=None if row[16] is None else str(row[16]).strip(),
            MAGLIVR=None if row[17] is None else str(row[17]).strip(),
            RETOUR_CDE=None if row[18] is None else str(row[18]).strip(),
            DTREC=row[19],
            DTFACT=row[20],
            FORMAT_EDI=None if row[21] is None else bool(row[21]),
            STATUTEDI=None if row[22] is None else str(row[22]).strip(),
        )


    @staticmethod
    def _build_lgcde(row: Any) -> Lgcde:
        """
        Build an Lgcde model from one SQL Server row.
        """

        return Lgcde(
            TYPCDE=str(row[0]).strip(),
            NOCDE=str(row[1]).strip(),
            CMARQ=str(row[2]).strip(),
            CCATEG=str(row[3]).strip(),
            CPROD=str(row[4]).strip(),
            PAAR=None if row[5] is None else float(row[5]),
            PAMP=None if row[6] is None else float(row[6]),
            QTESTK=None if row[7] is None else int(row[7]),
            QTECDE=None if row[8] is None else int(row[8]),
            TXREM=None if row[9] is None else float(row[9]),
            TVA=None if row[10] is None else float(row[10]),
            QTERECU=None if row[11] is None else int(row[11]),
            QTEREFUS=None if row[12] is None else int(row[12]),
            QTEFAC=None if row[13] is None else int(row[13]),
            MTLIG=None if row[14] is None else float(row[14]),
        )


    @staticmethod
    def _commande_parameters(
        commande: Commande,
    ) -> tuple[Any, ...]:
        """
        Return COMMANDE values in INSERT column order.
        """

        return (
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
            None if commande.CDECENTRAL is None
            else int(commande.CDECENTRAL),
            commande.TXREM,
            commande.MTCDE,
            commande.MTRECU,
            commande.MAGCDE,
            commande.MAGLIVR,
            commande.RETOUR_CDE,
            commande.DTREC,
            commande.DTFACT,
            None if commande.FORMAT_EDI is None
            else int(commande.FORMAT_EDI),
            commande.STATUTEDI,
        )