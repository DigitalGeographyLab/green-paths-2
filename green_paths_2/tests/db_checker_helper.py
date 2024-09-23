""" Generic test helper functions to check the integrity of a SQLite database after running a pipeline. """


def execute_query(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    # return the results
    results = cursor.fetchall()
    cursor.close()
    return results


def check_row_count(conn, table_name):
    cursor = conn.cursor()
    query = f"SELECT COUNT(*) FROM {table_name}"
    cursor.execute(query)
    actual_count = cursor.fetchone()[0]
    return actual_count


def check_row_exists(conn, table_name, column_name, value):
    cursor = conn.cursor()
    query = f"SELECT COUNT(*) FROM {table_name} WHERE {column_name} = ?"
    cursor.execute(query, (value,))
    result = cursor.fetchone()[0]
    return result > 0


def check_column_value_range(
    conn, table_name, column_name, min_value=None, max_value=None
):
    cursor = conn.cursor()
    query = f"SELECT {column_name} FROM {table_name}"
    cursor.execute(query)
    results = cursor.fetchall()

    for value in results:
        if min_value is not None and value[0] < min_value:
            return False
        if max_value is not None and value[0] > max_value:
            return False
    return True


def check_data_types(conn, table_name, column_name, expected_type):
    cursor = conn.cursor()

    # Check if the column exists
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [info[1] for info in cursor.fetchall()]

    # some columns might be missing in some rows
    if column_name not in columns:
        return True

    query = f"SELECT {column_name} FROM {table_name}"
    cursor.execute(query)
    results = cursor.fetchall()

    for value in results:
        if value[0] and not isinstance(value[0], expected_type):
            return False
    return True


def check_specific_value(conn, table_name, column_name, expected_value):
    cursor = conn.cursor()
    query = f"SELECT * FROM {table_name} WHERE {column_name} = ?"
    cursor.execute(query, (expected_value,))
    result = cursor.fetchone()
    return result is not None


def get_column_value_by_osm_id(conn, table_name, target_osm_id, column_name):
    cursor = conn.cursor()
    query = f"SELECT {column_name} FROM {table_name} WHERE osm_id = ?"
    cursor.execute(query, (target_osm_id,))
    result = cursor.fetchone()
    return result[0] if result else None


def check_geospatial_data(
    conn, table_name, column_name, expected_prefix="MULTILINESTRING"
):
    cursor = conn.cursor()
    query = f"SELECT {column_name} FROM {table_name}"
    cursor.execute(query)
    results = cursor.fetchall()

    for geom in results:
        if geom and geom[0] and not geom[0].startswith(expected_prefix):
            return False
    return True


def check_aggregated_results(conn, table_name, column_name, agg_func="SUM"):
    cursor = conn.cursor()
    query = f"SELECT {agg_func}({column_name}) FROM {table_name}"
    cursor.execute(query)
    result = cursor.fetchone()[0]
    return result


# TODO -> remove? should be emptied before and after all tests in conftest.py
# empty table
def empty_table(conn, table_name):
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {table_name};")
    conn.commit()
