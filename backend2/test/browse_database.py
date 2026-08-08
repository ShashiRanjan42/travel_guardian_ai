"""Interactive viewer for the tables and rows in wayfare.db.

Run from the backend directory:
    python test/browse_database.py
"""

from __future__ import annotations

import sqlite3
from pathlib import Path


DATABASE_PATH = Path(__file__).resolve().parents[1] / "wayfare.db"


def get_tables(connection: sqlite3.Connection) -> list[str]:
    """Return application tables, excluding SQLite's internal tables."""
    cursor = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
        """
    )
    return [row[0] for row in cursor.fetchall()]


def describe_table(connection: sqlite3.Connection, table_name: str) -> None:
    """Print the selected table's columns and every row."""
    print(f"\nTable: {table_name}")
    print("Columns:")
    for column in connection.execute(f'PRAGMA table_info("{table_name}")'):
        required = " NOT NULL" if column[3] else ""
        primary_key = " PRIMARY KEY" if column[5] else ""
        print(f"  - {column[1]}: {column[2]}{required}{primary_key}")

    rows = connection.execute(f'SELECT * FROM "{table_name}"').fetchall()
    print(f"\nRows ({len(rows)}):")
    if not rows:
        print("  (no rows)")
        return

    for number, row in enumerate(rows, start=1):
        print(f"\n  Row {number}")
        for column_name in row.keys():
            print(f"    {column_name}: {row[column_name]}")


def main() -> None:
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(f"Database not found: {DATABASE_PATH}")

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row
        tables = get_tables(connection)

        while True:
            print("\nWayfare database tables")
            for number, table_name in enumerate(tables, start=1):
                print(f"  {number}. {table_name}")
            print("  0. Exit")

            selection = input("\nSelect a table: ").strip()
            if selection == "0":
                print("Goodbye.")
                return

            try:
                table_name = tables[int(selection) - 1]
            except (ValueError, IndexError):
                print("Invalid selection. Enter a number from the menu.")
                continue

            describe_table(connection, table_name)
            input("\nPress Enter to return to the menu...")


if __name__ == "__main__":
    main()
