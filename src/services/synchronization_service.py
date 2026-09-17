"""
OrderSync

Module:
    synchronization_service.py

Location:
    src\\services

Description:
    Coordinates order synchronization from HyperFile to SQL Server.

Author:
    Joan Solé
"""

from dataclasses import dataclass
from datetime import date, timedelta
import logging

from models.commande import Commande
from models.lgcde import Lgcde

from repositories.hyperfile_repository import HyperFileRepository
from repositories.sqlserver_repository import SqlServerRepository


logger = logging.getLogger(__name__)


@dataclass
class SynchronizationStats:
    """
    Counters generated during one synchronization execution.
    """

    orders_read: int = 0
    orders_inserted: int = 0
    orders_updated: int = 0
    orders_unchanged: int = 0
    orders_finalized: int = 0
    orders_deleted: int = 0

    lines_read: int = 0
    lines_inserted: int = 0
    lines_updated: int = 0
    lines_unchanged: int = 0
    lines_deleted: int = 0

    orders_without_lines: int = 0


class SynchronizationService:
    """
    Synchronize COMMANDE and LGCDE records from HyperFile
    to SQL Server.
    """

    def __init__(
        self,
        source_repository: HyperFileRepository,
        destination_repository: SqlServerRepository,
        maj_periode: int,
    ) -> None:

        self._source = source_repository
        self._destination = destination_repository
        self._maj_periode = maj_periode


    def synchronize(self) -> SynchronizationStats:
        """
        Synchronize COMMANDE and LGCDE records.

        Synchronization rules:

            - Source record does not exist in SQL Server:
                INSERT.

            - Source record exists and is different:
                UPDATE.

            - Source record exists and is identical:
                UNCHANGED.

            - LGCDE exists in SQL Server but not in HyperFile
              for a COMMANDE returned by HyperFile:
                DELETE.

            - COMMANDE exists in SQL Server but is not returned
              by HyperFile:
                * inside update window -> DELETE;
                * outside update window -> set TYPCDE = 'V'.

        Returns:
            SynchronizationStats with execution counters.
        """

        stats = SynchronizationStats()

        # Keep the NOCDE values returned by HyperFile.
        # They will be used during the final reconciliation.
        source_nocdes: set[str] = set()

        logger.info("Order synchronization started.")

        for commande, lines in self._source.iter_orders_with_lines():

            stats.orders_read += 1
            source_nocdes.add(commande.NOCDE)

            self._synchronize_commande(
                commande,
                stats,
            )

            if not lines:
                stats.orders_without_lines += 1

            self._synchronize_lines(
                commande.NOCDE,
                lines,
                stats,
            )

            if stats.orders_read % 1000 == 0:
                logger.info(
                    "%d orders processed.",
                    stats.orders_read,
                )

        # Process COMMANDE records existing in SQL Server
        # but not returned by the HyperFile query.
        self._reconcile_missing_commandes(
            source_nocdes,
            stats,
        )

        logger.info(
            "Order synchronization completed. "
            "Orders read=%d, inserted=%d, updated=%d, "
            "unchanged=%d, finalized=%d, deleted=%d. "
            "Lines read=%d, inserted=%d, updated=%d, "
            "unchanged=%d, deleted=%d. "
            "Orders without lines=%d.",
            stats.orders_read,
            stats.orders_inserted,
            stats.orders_updated,
            stats.orders_unchanged,
            stats.orders_finalized,
            stats.orders_deleted,
            stats.lines_read,
            stats.lines_inserted,
            stats.lines_updated,
            stats.lines_unchanged,
            stats.lines_deleted,
            stats.orders_without_lines,
        )

        return stats


    def _synchronize_commande(
        self,
        commande: Commande,
        stats: SynchronizationStats,
    ) -> None:
        """
        Insert, update or leave unchanged one COMMANDE.
        """

        destination = self._destination.get_commande(
            commande.NOCDE
        )

        if destination is None:

            self._destination.insert_commande(
                commande
            )

            stats.orders_inserted += 1

            logger.debug(
                "COMMANDE inserted: NOCDE=%s",
                commande.NOCDE,
            )

            return

        if destination == commande:

            stats.orders_unchanged += 1
            return

        self._destination.update_commande(
            commande
        )

        stats.orders_updated += 1

        logger.debug(
            "COMMANDE updated: NOCDE=%s",
            commande.NOCDE,
        )


    def _synchronize_lines(
        self,
        nocde: str,
        source_lines: list[Lgcde],
        stats: SynchronizationStats,
    ) -> None:
        """
        Synchronize all LGCDE records belonging to one COMMANDE.

        SQL Server lines that no longer exist in HyperFile
        are deleted.
        """

        destination_lines = (
            self._destination.get_lgcde_for_commande(
                nocde
            )
        )

        for line in source_lines:

            stats.lines_read += 1

            key = line.line_key

            destination = destination_lines.pop(
                key,
                None,
            )

            if destination is None:

                self._destination.insert_lgcde(
                    line
                )

                stats.lines_inserted += 1

                logger.debug(
                    "LGCDE inserted: %s",
                    key,
                )

                continue

            if destination == line:

                stats.lines_unchanged += 1
                continue

            self._destination.update_lgcde(
                line
            )

            stats.lines_updated += 1

            logger.debug(
                "LGCDE updated: %s",
                key,
            )

        # Any remaining SQL Server line was not present
        # in HyperFile for this order.
        for key in destination_lines:

            self._destination.delete_lgcde(
                key
            )

            stats.lines_deleted += 1

            logger.debug(
                "LGCDE deleted: %s",
                key,
            )


    def _reconcile_missing_commandes(
        self,
        source_nocdes: set[str],
        stats: SynchronizationStats,
    ) -> None:
        """
        Process COMMANDE records existing in SQL Server but not
        returned by the HyperFile synchronization query.

        Rules:

            Inside the update window:
                The order should have been returned by HyperFile.
                Therefore, if it is missing, delete it.

            Outside the update window:
                A missing order is considered finalized and its
                TYPCDE is changed to 'V'.

        Orders already finalized ('V') outside the update window
        require no action.
        """

        filter_date = (
            date.today()
            - timedelta(weeks=self._maj_periode)
        )

        destination_commandes = (
            self._destination.get_commandes_for_reconciliation()
        )

        for commande in destination_commandes:

            if commande.NOCDE in source_nocdes:
                continue

            # --------------------------------------------------
            # Missing order inside the synchronization window.
            # --------------------------------------------------

            if commande.DTCDE >= filter_date:

                self._destination.delete_commande(
                    commande.NOCDE
                )

                stats.orders_deleted += 1

                logger.warning(
                    "COMMANDE deleted because it no longer "
                    "exists in HyperFile: NOCDE=%s DTCDE=%s",
                    commande.NOCDE,
                    commande.DTCDE,
                )

                continue

            # --------------------------------------------------
            # Missing order outside the synchronization window.
            #
            # If it was not returned by HyperFile, it has reached
            # the final state V.
            # --------------------------------------------------

            if commande.TYPCDE != "V":

                self._destination.finalize_commande(
                    commande.NOCDE
                )

                stats.orders_finalized += 1

                logger.debug(
                    "COMMANDE finalized: "
                    "NOCDE=%s DTCDE=%s",
                    commande.NOCDE,
                    commande.DTCDE,
                )