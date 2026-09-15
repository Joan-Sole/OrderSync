"""
OrderSync

Module:
    database_validator_commande.py

Location:
    src\\tools

Description:
    Compare HyperFile COMMANDE table against SQL Server destination tables.

Author:
    Joan Solé

invocation from src folder: python -m tools.database_validator_commande --keys NOCDE --fields DTCDE CLICDE MAGCDE
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import logging
from datetime import date, timedelta
import argparse
from core.settings  import load_settings
from core.sqlserver import SqlServerConnection
from core.hyperfile import HyperFileConnection


logger = logging.getLogger(__name__)

DEFAULT_DATE_FIELD:str ='DTCDE'


@dataclass
class TableComparisonResult:
    table: str
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

    def _read_sqlserver(
        self,
        table: str,
        fields: tuple[str, ...],
        condition: str | None = None,
    ) -> list[dict[str, Any]]:

        field_list = ", ".join(fields)
        query = f"""
            SELECT {field_list}
            FROM {table} {f"WHERE {condition}" if condition else ""}
        """
        cursor = self._sqlserver.execute(query)

        try:
            rows = cursor.fetchall()
            return [
                dict(zip(fields, row))
                for row in rows
            ]
        finally:
            cursor.close()


    def _read_hyperfile(
        self,
        table: str,
        fields: tuple[str, ...],
        condition: str | None = None,
    ) -> list[dict[str, Any]]:

        field_list = ", ".join(fields)
        query = f"""
            SELECT {field_list}
            FROM {table} {f"WHERE {condition}" if condition else ""}
        """
        recordset = self._hyperfile.execute(query)

        try:
            rows = []
            while not recordset.EOF:
                row = {
                    field: recordset.Fields(field).Value
                    for field in fields
                }
                rows.append(row)
                recordset.MoveNext()
            return rows
        finally:
            recordset.Close()

    def compare_table(
        self,
        table: str,
        key_fields: tuple[str, ...],
        compare_fields: tuple[str, ...],
        weeks: int=30,  # Number of weeks to look back for comparison
        key_time: str  = 'DTCDE',
    ) -> TableComparisonResult:

        fields = key_fields + compare_fields

        logger.info("Comparing table %s", table)
        logger.info("Key fields: %s", ", ".join(key_fields))
        logger.info("Other fields to compare: %s", ", ".join(compare_fields))

        if weeks <= 0:
            raise ValueError("Weeks must be a positive integer")

        filter_date = date.today() - timedelta(weeks=weeks)
        condition = (
            f"{key_time} >= '{filter_date.strftime('%Y%m%d')}'"
        )
        logger.info("Condition: %s", condition)

        hyperfile_rows = self._read_hyperfile(
            table,
            fields,
            condition=condition
        )

        sqlserver_rows = self._read_sqlserver(
            table,
            fields,
            condition=condition
        )

        hf_index = {
            self._make_key(row, key_fields): row
            for row in hyperfile_rows
        }

        sql_index = {
            self._make_key(row, key_fields): row
            for row in sqlserver_rows
        }

        hf_keys = set(hf_index)
        sql_keys = set(sql_index)

        missing = sorted(hf_keys - sql_keys)
        extra = sorted(sql_keys - hf_keys)

        common_keys = hf_keys & sql_keys

        different_rows = []

        for key in common_keys:

            hf_row = hf_index[key]
            sql_row = sql_index[key]

            differences = {}

            for field in compare_fields:

                hf_value = self._normalize(hf_row[field])
                sql_value = self._normalize(sql_row[field])

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
            table=table,
            hyperfile_count=len(hyperfile_rows),
            sqlserver_count=len(sqlserver_rows),
            missing_in_sqlserver=missing,
            extra_in_sqlserver=extra,
            different_rows=different_rows,
        )


    @staticmethod
    def _make_key(
        row: dict[str, Any],
        key_fields: tuple[str, ...]
    ) -> tuple:

        return tuple(
            DatabaseValidator._normalize(row[field])
            for field in key_fields
        )


    @staticmethod
    def _normalize(value: Any) -> Any:

        if isinstance(value, str):
            return value.strip()

        return value

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Validate database tables."
    )

    parser.add_argument(
        "--keys",
        nargs="+",
        required=True,
        help="The key fields for the table."
    )

    parser.add_argument(
        "--fields",
        nargs="+",
        required=True,
        help="The fields to compare."
    )

    args = parser.parse_args()

    # script location /OrderSync/src/main.py  target location /OrderSync
    project_root = Path(__file__).resolve().parents[2]
	# final target location /OrderSync/config
    config_directory = project_root / "config"
    config_file = config_directory / "config.yaml"
    settings = load_settings(config_file)
    CHECK_PERIOD_WEEKS = settings.application.maj_periode

    with HyperFileConnection(settings) as hyperfile_connection, SqlServerConnection(settings) as sqlserver_connection:
        validator = DatabaseValidator(hyperfile_connection, sqlserver_connection)
        result = validator.compare_table(
            table="COMMANDE",
            key_fields=tuple(args.keys),
            compare_fields=tuple(args.fields),
            weeks=CHECK_PERIOD_WEEKS,
            key_time=DEFAULT_DATE_FIELD
        )

    print(result)
