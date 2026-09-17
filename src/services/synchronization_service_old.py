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
import logging

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
    orders_existing: int = 0

    lines_read: int = 0
    lines_inserted: int = 0
    lines_existing: int = 0

    orders_without_lines: int = 0


class SynchronizationService:
    """
    Synchronize orders and order lines from HyperFile
    to SQL Server.
    """

    def __init__(
        self,
        source_repository: HyperFileRepository,
        destination_repository: SqlServerRepository,
    ) -> None:

        self._source = source_repository
        self._destination = destination_repository


    def synchronize(self) -> SynchronizationStats:
        """
        Synchronize COMMANDE and LGCDE records.

        Current version:
            - inserts new COMMANDE records;
            - inserts new LGCDE records;
            - leaves existing records unchanged.

        Returns:
            SynchronizationStats with execution counters.
        """

        stats = SynchronizationStats()

        logger.info("Order synchronization started.")

        for commande, lines in self._source.iter_orders_with_lines():

            stats.orders_read += 1

            self._synchronize_commande(
                commande,
                stats,
            )

            if not lines:
                stats.orders_without_lines += 1

            for line in lines:

                stats.lines_read += 1

                self._synchronize_line(
                    line,
                    stats,
                )

            if stats.orders_read % 1000 == 0:
                logger.info(
                    "%d orders processed.",
                    stats.orders_read,
                )

        logger.info(
            "Order synchronization completed. "
            "Orders read=%d, inserted=%d, existing=%d. "
            "Lines read=%d, inserted=%d, existing=%d. "
            "Orders without lines=%d.",
            stats.orders_read,
            stats.orders_inserted,
            stats.orders_existing,
            stats.lines_read,
            stats.lines_inserted,
            stats.lines_existing,
            stats.orders_without_lines,
        )

        return stats


    def _synchronize_commande(
        self,
        commande,
        stats: SynchronizationStats,
    ) -> None:
        """
        Insert a COMMANDE record if it does not already exist.
        """

        if self._destination.commande_exists(
            commande.NOCDE
        ):
            stats.orders_existing += 1
            return

        self._destination.insert_commande(
            commande
        )

        stats.orders_inserted += 1

        logger.debug(
            "COMMANDE inserted: NOCDE=%s",
            commande.NOCDE,
        )


    def _synchronize_line(
        self,
        line,
        stats: SynchronizationStats,
    ) -> None:
        """
        Insert an LGCDE record if it does not already exist.
        """

        if self._destination.lgcde_exists(
            line.NOCDE,
            line.CMARQ,
            line.CCATEG,
            line.CPROD,
        ):
            stats.lines_existing += 1
            return

        self._destination.insert_lgcde(
            line
        )

        stats.lines_inserted += 1

        logger.debug(
            "LGCDE inserted: "
            "NOCDE=%s CMARQ=%s CCATEG=%s CPROD=%s",
            line.NOCDE,
            line.CMARQ,
            line.CCATEG,
            line.CPROD,
        )