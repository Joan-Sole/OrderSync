"""
OrderSync

Module:
    database_validator_lgcde.py

Location:
    src

Description:
    Compare HyperFile LGCDE table against SQL Server LGCDE table
    for orders belonging to the maj_periode period.

Author:
    Joan Solé
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import logging
from datetime import date, datetime, timedelta
import argparse

from core.settings import load_settings
from core.sqlserver import SqlServerConnection
from core.hyperfile import HyperFileConnection
from core.logger import initialise_logger


logger = logging.getLogger(__name__)

DEFAULT_DATE_FIELD: str = "DTCDE"

LGCDE_KEY_FIELDS: tuple[str, ...] = (
    "NOCDE",
    "CMARQ",
    "CCATEG",
    "CPROD",
)


@dataclass
class TableComparisonResult:
    table: str
    commandes_count: int
    hyperfile_count: int
    sqlserver_count: int
    missing_in_sqlserver: list[tuple]
    extra_in_sqlserver: list[tuple]
    different_rows: list[dict]


class DatabaseValidator:

    def __init__(
        self,
        hyperfile_connection,
        sqlserver_connection,
    ) -> None:

        self._hyperfile = hyperfile_connection
        self._sqlserver = sqlserver_connection

    def _read_hyperfile_commandes(
        self,
        weeks: int,
        key_time: str = DEFAULT_DATE_FIELD,
    ) -> set[str]:
        """
        Return the NOCDE values from HyperFile COMMANDE
        belonging to maj_periode.
        """

        if weeks <= 0:
            raise ValueError("Weeks must be a positive integer")

        filter_date = date.today() - timedelta(weeks=weeks)

        condition = (
            f"{key_time} >= "
            f"'{filter_date.strftime('%Y%m%d')}'"
        )

        query = f"""
            SELECT NOCDE
            FROM COMMANDE
            WHERE {condition}
        """

        logger.info(
            "Selecting COMMANDE records with condition: %s",
            condition,
        )

        recordset = self._hyperfile.execute(query)

        try:
            nocdes: set[str] = set()

            while not recordset.EOF:

                value = recordset.Fields("NOCDE").Value

                if value is not None:

                    nocde = str(value).strip()

                    if nocde:
                        nocdes.add(nocde)

                recordset.MoveNext()

            return nocdes

        finally:
            recordset.Close()

    def _read_hyperfile_lgcde(
        self,
        fields: tuple[str, ...],
        nocdes: set[str],
    ) -> list[dict[str, Any]]:
        """
        Read HyperFile LGCDE and keep only lines belonging
        to the selected COMMANDE records.
        """

        field_list = ", ".join(fields)

        query = f"""
            SELECT {field_list}
            FROM LGCDE
        """

        recordset = self._hyperfile.execute(query)

        try:
            rows: list[dict[str, Any]] = []

            while not recordset.EOF:

                nocde_value = (
                    recordset.Fields("NOCDE").Value
                )

                nocde = (
                    str(nocde_value).strip()
                    if nocde_value is not None
                    else ""
                )

                if nocde in nocdes:

                    row = {
                        field:
                            recordset.Fields(field).Value
                        for field in fields
                    }

                    rows.append(row)

                recordset.MoveNext()

            return rows

        finally:
            recordset.Close()

    def _read_sqlserver_lgcde(
        self,
        fields: tuple[str, ...],
        nocdes: set[str],
    ) -> list[dict[str, Any]]:
        """
        Read SQL Server LGCDE records belonging to the
        selected HyperFile COMMANDE records.
        """

        if not nocdes:
            return []

        field_list = ", ".join(fields)

        rows: list[dict[str, Any]] = []

        # SQL Server has a maximum number of parameters
        # per statement. Process NOCDE values in batches.
        batch_size = 1000

        nocde_list = list(nocdes)

        for start in range(
            0,
            len(nocde_list),
            batch_size,
        ):

            batch = nocde_list[
                start:start + batch_size
            ]

            placeholders = ", ".join(
                "?" for _ in batch
            )

            query = f"""
                SELECT {field_list}
                FROM LGCDE
                WHERE NOCDE IN ({placeholders})
            """

            cursor = self._sqlserver.execute(
                query,
                tuple(batch),
            )

            try:

                rows.extend(
                    dict(zip(fields, row))
                    for row in cursor.fetchall()
                )

            finally:
                cursor.close()

        return rows

    def compare_table(
        self,
        compare_fields: tuple[str, ...],
        weeks: int = 30,
    ) -> TableComparisonResult:

        duplicated_fields = (
            set(LGCDE_KEY_FIELDS)
            & set(compare_fields)
        )

        if duplicated_fields:

            raise ValueError(
                "Fields cannot be both key and "
                "compare fields: "
                f"{', '.join(sorted(duplicated_fields))}"
            )

        fields = (
            LGCDE_KEY_FIELDS
            + compare_fields
        )

        logger.info("Comparing table LGCDE")

        logger.info(
            "Key fields: %s",
            ", ".join(LGCDE_KEY_FIELDS),
        )

        logger.info(
            "Other fields to compare: %s",
            ", ".join(compare_fields),
        )

        #
        # 1. Obtain COMMANDE keys belonging to maj_periode
        #

        nocdes = self._read_hyperfile_commandes(
            weeks=weeks,
            key_time=DEFAULT_DATE_FIELD,
        )

        logger.info(
            "%d COMMANDE records selected.",
            len(nocdes),
        )

        #
        # 2. Read corresponding HyperFile LGCDE rows
        #

        hyperfile_rows = (
            self._read_hyperfile_lgcde(
                fields,
                nocdes,
            )
        )

        logger.info(
            "%d HyperFile LGCDE records selected.",
            len(hyperfile_rows),
        )

        #
        # 3. Read corresponding SQL Server LGCDE rows
        #

        sqlserver_rows = (
            self._read_sqlserver_lgcde(
                fields,
                nocdes,
            )
        )

        logger.info(
            "%d SQL Server LGCDE records selected.",
            len(sqlserver_rows),
        )

        #
        # 4. Build indexes using the LGCDE unique key
        #

        hf_index = {
            self._make_key(
                row,
                LGCDE_KEY_FIELDS,
            ): row
            for row in hyperfile_rows
        }

        sql_index = {
            self._make_key(
                row,
                LGCDE_KEY_FIELDS,
            ): row
            for row in sqlserver_rows
        }

        hf_keys = set(hf_index)
        sql_keys = set(sql_index)

        #
        # 5. Missing / extra lines
        #

        missing = sorted(
            hf_keys - sql_keys
        )

        extra = sorted(
            sql_keys - hf_keys
        )

        #
        # 6. Compare common lines
        #

        common_keys = (
            hf_keys & sql_keys
        )

        different_rows = []

        for key in common_keys:

            hf_row = hf_index[key]
            sql_row = sql_index[key]

            differences = {}

            for field in compare_fields:

                hf_value = self._normalize(
                    hf_row[field]
                )

                sql_value = self._normalize(
                    sql_row[field]
                )

                if hf_value != sql_value:

                    differences[field] = {
                        "hyperfile": hf_value,
                        "sqlserver": sql_value,
                    }

            if differences:

                different_rows.append({
                    "key": key,
                    "differences": differences,
                })

        return TableComparisonResult(
            table="LGCDE",
            commandes_count=len(nocdes),
            hyperfile_count=len(
                hyperfile_rows
            ),
            sqlserver_count=len(
                sqlserver_rows
            ),
            missing_in_sqlserver=missing,
            extra_in_sqlserver=extra,
            different_rows=different_rows,
        )

    @staticmethod
    def _make_key(
        row: dict[str, Any],
        key_fields: tuple[str, ...],
    ) -> tuple:

        return tuple(
            DatabaseValidator._normalize(
                row[field]
            )
            for field in key_fields
        )

    @staticmethod
    def _normalize(
        value: Any,
    ) -> Any:

        if isinstance(value, str):
            return value.strip()

        if isinstance(value, datetime):
            return value.strftime("%Y%m%d")

        if isinstance(value, date):
            return value.strftime("%Y%m%d")

        return value


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Validate LGCDE database tables."
    )

    parser.add_argument(
        "--fields",
        nargs="+",
        required=True,
        help="The fields to compare.",
    )

    args = parser.parse_args()

    # Script location:
    # /OrderSync/src/database_validator_lgcde.py
    #
    # Target location:
    # /OrderSync

    project_root = (
        Path(__file__).resolve().parents[1]
    )

    config_directory = (
        project_root / "config"
    )

    config_file = (
        config_directory / "config.yaml"
    )

    settings = load_settings(
        config_file
    )

    initialise_logger(settings)

    logger.info(
        "Checking LGCDE tables matching"
    )

    check_period_weeks = int(
        settings.application.maj_periode
    )

    with (
        HyperFileConnection(settings)
        as hyperfile_connection,

        SqlServerConnection(settings)
        as sqlserver_connection,
    ):

        validator = DatabaseValidator(
            hyperfile_connection,
            sqlserver_connection,
        )

        result = validator.compare_table(
            compare_fields=tuple(
                args.fields
            ),
            weeks=check_period_weeks,
        )

    print(result)

    logger.info(
        "Finished checking LGCDE tables matching. "
        "Result: %s",
        result,
    )