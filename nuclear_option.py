import sqlite3 as sql
import sys

db_filename = sys.argv[1] if len(sys.argv) > 1 else 'my-budget-default.sqlite'

db = sql.connect(db_filename)

crsr = db.cursor()
crsr.execute("SELECT name FROM sqlite_master WHERE type='table';")

for table in crsr.fetchall() :
    crsr.execute('DROP TABLE {};'.format(table[0]))

db.commit()

db.close()
