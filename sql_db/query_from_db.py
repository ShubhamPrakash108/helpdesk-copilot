import sqlite3

def fetch_data_from_db(ID,db_path="customer_concern.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT subject, body FROM customer_concern WHERE id = ?", (ID,))
    
    data = cursor.fetchall()
    conn.close()
    return data

# print("Subject:")
# print(fetch_data_from_db("TICKET-256")[0][0])
# print("Body:")
# print(fetch_data_from_db("TICKET-256")[0][1])