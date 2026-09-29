import sqlite3
conn = sqlite3.connect('D:/Antigravity/SIH-26-Criminal-Network-Analysis/backend/demo_sih26190.db')
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
for t in tables:
    print(t[0])
    cols = conn.execute(f"PRAGMA table_info({t[0]})").fetchall()
    for c in cols:
        print("  ", c[1], c[2])
