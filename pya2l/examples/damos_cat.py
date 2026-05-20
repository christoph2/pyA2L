import os
import sqlite3
import subprocess
import sys
from pathlib import Path


PTH = r"e:\damos"
PTH = r"c:\csprojects"


class DB:

    def __init__(self, fname: str):
        try:
            os.unlink(fname)
        except Exception as e:
            print(f"{e}")
        self.conn = sqlite3.connect(fname)
        self.cur = self.conn.cursor()
        self.create_schema()

    def __del__(self):
        self.close()

    def close(self):
        self.conn.close()

    def get_category(self, name):
        res = self.cur.execute("SELECT id  FROM category WHERE NAME=?;", (name,))
        rows = res.fetchone()
        if not rows:
            res = self.cur.execute("INSERT INTO category(name) VALUES(?)", (name,))
            self.conn.commit()
            res = self.cur.execute("SELECT id  FROM category WHERE NAME=?;", (name,))
            rows = res.fetchone()
            return rows[0]
        return rows[0]

    def add(self, name, ext, cat_id):
        res = self.cur.execute(
            "INSERT INTO file(name, ext, cat) VALUES(?, ?, ?)",
            (
                name,
                ext,
                cat_id,
            ),
        )
        self.conn.commit()

    def create_schema(self):
        self.cur.execute("""PRAGMA foreign_keys=ON;""")
        self.cur.execute("""CREATE TABLE IF NOT EXISTS category(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
        """)
        self.cur.execute("""CREATE TABLE IF NOT EXISTS file(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            ext TEXT NOT NULL,
            cat INTEGER NOT NULL,
            FOREIGN KEY(cat) REFERENCES category(id)
        )
        """)
        self.conn.commit()


db = DB("damos_cat.sqlite3")


def recurse(pth):
    for phile in pth.iterdir():
        if phile.is_dir():
            recurse(phile)
            try:
                print(phile)
            except:
                pass
        else:
            try:
                output = subprocess.getoutput(
                    f"file -b {phile}"
                )  # nosec B605 — example script; path comes from local filesystem walk
                descr = output
                category = output.split(",")[0]
                cat_id = db.get_category(category)
                ext = phile.suffix
                db.add(str(phile), ext, cat_id)
                sys.exit()
            except Exception as e:
                print(f"{e}")


recurse(Path(PTH))
db.close()
