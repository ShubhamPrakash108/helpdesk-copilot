import sqlite3
import json

conn = sqlite3.connect("customer_concern.db")
cursor = conn.cursor()

with open("./json_files_data/data.json", "r") as f:
    tickets = json.load(f)

cursor.execute("""
CREATE TABLE IF NOT EXISTS customer_concern (
    id TEXT PRIMARY KEY,
    subject TEXT,
    body TEXT
)
""")


def insert_to_db(tickets):
    for ticket in tickets:
        cursor.execute("""
        INSERT OR REPLACE INTO customer_concern (id, subject, body)
        VALUES (?, ?, ?)
        """, (ticket["id"], ticket["subject"], ticket["body"]))

    conn.commit()
    conn.close()


insert_to_db(tickets)


conn.close()