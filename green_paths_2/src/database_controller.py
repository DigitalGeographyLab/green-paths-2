import os
from collections import defaultdict
import sqlite3
from typing import Dict, List, Any, Optional, Tuple

from ..src.config import GP2_DB_PATH, GP2_DB_TEST_PATH, SEGMENT_STORE_TABLE
from ..src.timer import time_logger


class DatabaseController:
    def __init__(self):
        self._set_db_path()

    def _set_db_path(self):
        if os.getenv("ENV") == "TEST":
            self.db_path = GP2_DB_TEST_PATH
        else:
            self.db_path = GP2_DB_PATH

    def connect(self):
        return sqlite3.connect(self.db_path)

    # empty table
    def empty_table(self, table: str):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {table}")
        conn.commit()
        conn.close()

    def drop_table(self, table: str):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(f"DROP TABLE IF EXISTS {table}")
        conn.commit()
        conn.close()

    # TODO: put force as parameter bool
    def create_table_from_dict_data(
        self, table: str, data: Dict[str, Any], force: bool = False
    ):
        """Drops targe table if exists and then creates db tables based on dict data"""
        # drop the table if it already exists
        # for the tables can have different columns
        if force:
            self.drop_table(table)
        columns = []
        for key, value in data.items():
            if key == "osm_id":
                columns.append(f"{key} INTEGER PRIMARY KEY")
            elif key == "geometry":
                columns.append(f"{key} TEXT")
            elif isinstance(value, float):
                columns.append(f"{key} REAL")
            elif isinstance(value, int):
                columns.append(f"{key} INTEGER")
            else:
                columns.append(f"{key} TEXT")
        columns_str = ", ".join(columns)
        create_table_sql = f"CREATE TABLE IF NOT EXISTS {table} ({columns_str})"

        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(create_table_sql)
        conn.commit()
        conn.close()

    @time_logger
    def create_table_from_params(self, table: str, columns: List[Dict[str, str]]):
        # Drop the table if it already exists
        self.drop_table(table)

        columns_str = ", ".join([f"{col['name']} {col['type']}" for col in columns])
        create_table_sql = f"CREATE TABLE IF NOT EXISTS {table} ({columns_str})"

        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(create_table_sql)
        conn.commit()
        conn.close()

    def add_single(self, table: str, data: Dict[str, Any]):
        keys = data.keys()
        columns = ", ".join(keys)
        placeholders = ", ".join(["?" for _ in keys])
        values = tuple(data[key] if data[key] is not None else None for key in keys)

        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(
            f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", values
        )
        conn.commit()
        conn.close()

    @time_logger
    def add_many_dict(
        self, table: str, data: Dict[str, Dict[str, Any]], chunk_size: int = 10000
    ) -> None:
        """
        Add many records to the database from a dictionary of dictionaries

        Parameters
        ----------
        table : str
            The table to add the records to.
        data : Dict[str, Dict[str, Any]]
            The data to add to the table.
        chunk_size : int
            The size of the chunks to add to the database.
        """

        if not data:
            return
        keys = next(iter(data.values())).keys()
        columns = ", ".join(keys)
        placeholders = ", ".join(["?" for _ in keys])

        values_list = [tuple(d.values()) for d in data.values()]

        conn = self.connect()
        cursor = conn.cursor()
        for i in range(0, len(values_list), chunk_size):
            chunk = values_list[i : i + chunk_size]
            cursor.executemany(
                f"INSERT OR IGNORE INTO {table} ({columns}) VALUES ({placeholders})",
                chunk,
            )
            conn.commit()
        conn.close()

    def get_all_columns(self, table: str) -> List[str]:
        """
        Get all columns from a table

        Parameters
        ----------
        table : stro
            The table to get the columns from.
        """
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table});")
        columns = [col[1] for col in cursor.fetchall()]
        conn.close()
        return columns

    def normalize_data(
        self, data: List[Dict[str, Any]], all_columns: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Normalize data to have the same columns as the table, add None to those that are missing.
        This has to be done in order to be able to add paths with missing columns to the database.

        Parameters
        ----------
        data : List[Dict[str, Any]]
            The data to normalize.
        all_columns : List[str]
            The columns to normalize the data to.
        """
        normalized_data = []
        for item in data:
            normalized_item = {col: item.get(col, None) for col in all_columns}
            normalized_data.append(normalized_item)
        return normalized_data

    def add_many_list(self, table: str, data: List[Dict[str, Any]]) -> None:
        """
        Add many records to the database from list of dictionaries

        Parameters
        ----------
        table : str
            The table to add the records to.
        data : List[Dict[str, Any]]
            The data to add to the table.
        """
        if not data:
            return

        # Assuming all dicts have the same keys
        all_columns = self.get_all_columns(table)
        normalized_data = self.normalize_data(data, all_columns)

        keys = all_columns
        columns = ", ".join(keys)
        placeholders = ", ".join(["?" for _ in keys])

        values_list = [tuple(d.values()) for d in normalized_data]

        conn = self.connect()
        cursor = conn.cursor()
        cursor.executemany(
            f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", values_list
        )
        conn.commit()
        conn.close()

    def get_normalized_exposures_by_column_from_segment_table(
        self, target_column: str
    ) -> Dict[str, float]:
        """Get normalized exposures by column from the database.

        Parameters
        ----------
        target_column : str
            The target column to get the normalized exposures from.

        Returns
        -------
        Dict[str, float]
            A dictionary where the keys are the OSM IDs and the values are the normalized exposures.
        """
        conn = self.connect()
        cursor = conn.cursor()

        query = f"SELECT osm_id, {target_column} FROM {SEGMENT_STORE_TABLE}"
        cursor.execute(query)
        result = {}
        for row in cursor.fetchall():
            # Ensure the key is a string
            osm_id = str(row[0])
            target_value = row[1]
            # Ensure the value is a float, handle NoneType gracefully
            try:
                target_value = float(target_value)
            except (ValueError, TypeError):
                # Handle or skip None values as needed
                target_value = None
            if target_value is not None:
                result[osm_id] = target_value
            conn.close()
        return result

    # get multiple records by column values

    # Function to select rows based on one or many osm_id values
    # Function to select rows based on one or many osm_id values
    def select_rows_by_osm_ids(
        self,
        table: str,
        osm_ids: List[int],
        columns: Optional[List[str]] = None,  # Optional parameter for column selection
    ) -> List[dict]:
        conn = self.connect()
        cursor = conn.cursor()

        # Determine which columns to select
        if columns:
            columns_str = ", ".join(columns)
        else:
            columns_str = "*"

        placeholders = ", ".join(["?"] * len(osm_ids))
        query = f"SELECT {columns_str} FROM {table} WHERE osm_id IN ({placeholders})"
        cursor.execute(query, osm_ids)
        rows = cursor.fetchall()
        conn.close()
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in rows]

    def fetch_batch(self, table: str, limit: int, offset: int) -> List[Dict[str, Any]]:
        conn = self.connect()
        query = f"SELECT * FROM {table} LIMIT ? OFFSET ?"
        cursor = conn.cursor()
        cursor.execute(query, (limit, offset))
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        conn.close()
        return [dict(zip(columns, row)) for row in rows]

    def get_all(
        self, table: str, column_names: bool = False
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()

        # Fetch column names if required
        if column_names:
            column_names = [description[0] for description in cursor.description]
            # Convert rows to list of dictionaries
            rows = [dict(zip(column_names, row)) for row in rows]
        else:
            column_names = None
            # Otherwise keep rows as list of tuples
            rows = [tuple(row) for row in rows]

        conn.close()
        return rows, column_names

    def get_row_count(self, table: str) -> int:
        conn = self.connect()
        query = f"SELECT COUNT(*) FROM {table}"
        cursor = conn.cursor()
        cursor.execute(query)
        count = cursor.fetchone()[0]
        return count

    def create_index(self, table, column):
        # Query to check if the index already exists
        conn = self.connect()
        cursor = conn.cursor()
        index_name = (
            f"{column}_index"  # You might have a naming convention for your indexes
        )
        # Check if the index already exists
        cursor.execute(f"PRAGMA index_list({table});")
        existing_indexes = [
            index[1] for index in cursor.fetchall()
        ]  # index[1] is the index name in the result

        if index_name not in existing_indexes:
            # Only create the index if it doesn't already exist
            cursor.execute(f"CREATE INDEX {index_name} ON {table}({column});")
            conn.commit()

    def get_existing_columns(self, table_name):
        """
        Get the list of existing columns in a table.

        :param table_name: Name of the table.
        :return: A set of existing column names.
        """
        conn = self.connect()
        cursor = conn.cursor()

        # Fetch all column names for the table
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns_info = cursor.fetchall()

        # Extract column names from the info and close the connection
        existing_columns = {info[1] for info in columns_info}
        conn.close()
        return existing_columns

    def add_column_if_not_exists(self, table_name, column_name, column_type="TEXT"):
        # Query to check if the column exists
        conn = self.connect()
        cursor = conn.cursor()
        query = cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in query.fetchall()]

        # Check if the column is already in the table
        if column_name not in columns:
            # If not, add the column
            cursor.execute(
                f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type};"
            )

    def check_table_exists(self, table_name):
        """
        Checks if a table exists in an SQLite3 database.

        :param db_name: Name of the database file.
        :param table_name: Name of the table to check.
        :return: True if the table exists, False otherwise.
        """
        # Connect to the SQLite database (or create it if it doesn't exist)
        conn = self.connect()
        cursor = conn.cursor()

        # Query to check if the table exists
        cursor.execute(
            """
            SELECT name 
            FROM sqlite_master 
            WHERE type='table' AND name=?;
        """,
            (table_name,),
        )
        result = cursor.fetchone()
        conn.close()
        return result is not None


# todo -> maybe move elsewhere:
def split_data_by_length(
    data: Dict[str, Dict[str, Any]]
) -> Dict[int, Dict[str, Dict[str, Any]]]:
    """
    Splits the data into subsets based on the number of keys in each record.

    :param data: The data dictionary to split.
    :return: A dictionary where the keys are the lengths and the values are dictionaries of records with that length.
    """
    split_data = defaultdict(dict)

    for record_id, record in data.items():
        length = len(record)
        split_data[length][record_id] = record

    return split_data
