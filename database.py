import sqlite3
import json

TABLE_CONFIG = "./table_config.json"


class SQLiteManager:
    conn: sqlite3.Connection

    def __init__(self, database: str) -> None:
        try:
            self.conn = sqlite3.connect(database)

            cur = self.conn.cursor()
            cur.execute("PRAGMA strict=ON;")
            cur.close()

            print(f"Opened SQLite connection to {database}")
        except sqlite3.Error as e:
            print(e)

    def create_tables(self) -> None:
        cur = self.conn.cursor()

        # Reads tables from TABLE_CONFIG file
        table_config = json.load(open(TABLE_CONFIG, "r"))
        for table in table_config["tables"]:
            name = table["name"]
            print(f"Creating table {name}")
            cur.execute(f"DROP TABLE IF EXISTS {name}")
            MAKE_SQL = f"CREATE TABLE {name} ("
            for column in table["columns"]:
                MAKE_SQL += f"{column}, "

            MAKE_SQL = MAKE_SQL[:-2] + ");"  # Remove trailing comma
            cur.execute(MAKE_SQL)

        cur.close()


if __name__ == "__main__":
    db = SQLiteManager("./test.db")

    db.create_tables()