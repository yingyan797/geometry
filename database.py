import sqlite3
import numpy as np

class Database:
    def __init__(self, dbname="data.db"):
        self.name = dbname
    def start(self):
        self.con = sqlite3.connect(self.name)
        self._create_tables()

    def do(self, instr):
        self.con.execute(instr)

    def _create_tables(self):
        self.do("create table if not exists History (Title text, Width integer, Height integer, Palette text, Canvas text)")

    def read_all(self, instr):
        return self.con.execute(instr).fetchall()
    def read_one(self, instr):
        return self.con.execute(instr).fetchone()

    def save(self):
        self.con.commit()
        self.con.close()

if __name__ == "__main__":
    db = Database()
    db.start()
    print(db.read_all("select rowid from History"))
    # db.do("update History set rowid=rowid-1")
    db.save()
    # code = "12345678900010203040506"
    # print(canvas_decode(code, 4,4))
    # pal = "ff000000ffff"
    # print([pal[i:i+6] for i in range(0,len(pal),6)])
