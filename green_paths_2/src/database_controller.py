import sqlite3
from typing import List, Tuple, Any
from shapely.wkt import dumps, loads


class DatabaseController:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def connect(self):
        return sqlite3.connect(self.db_path)

    def create_table(self, create_table_sql: str):
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute(create_table_sql)
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print(e)

    def add_one(self, table: str, columns: Tuple[str], values: Tuple[Any]):
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute(
                f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(['?' for _ in values])})",
                values,
            )
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print(e)

    def add_many(self, table: str, columns: Tuple[str], values_list: List[Tuple[Any]]):
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.executemany(
                f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(['?' for _ in values_list[0]])})",
                values_list,
            )
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print(e)

    def get_all(self, table: str):
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            conn.close()
            return rows
        except sqlite3.Error as e:
            print(e)
            return []


# # Usage example
# if __name__ == "__main__":
#     db_handler = SQLiteHandler('routing_data.db')

#     create_table_sql = '''
#     CREATE TABLE IF NOT EXISTS routing_data (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         name TEXT NOT NULL,
#         geom TEXT NOT NULL
#     );
#     '''
#     db_handler.create_table(create_table_sql)

#     # Adding one record
#     db_handler.add_one('routing_data', ('name', 'geom'), ('example_point', dumps(Point(1.0, 2.0))))

#     # Adding multiple records
#     points = [('point1', dumps(Point(2.0, 3.0))), ('point2', dumps(Point(3.0, 4.0)))]
#     db_handler.add_many('routing_data', ('name', 'geom'), points)

#     # Retrieving all records
#     records = db_handler.get_all('routing_data')
#     print(records)
