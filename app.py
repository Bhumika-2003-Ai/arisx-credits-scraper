from fastapi import FastAPI
import sqlite3

app = FastAPI()


@app.get("/")
def home():
    return {"message": "API running"}


@app.get("/programs")
def get_programs():
    conn = sqlite3.connect("credits.db")
    conn.row_factory = sqlite3.Row  # ✅ IMPORTANT (returns dict-like rows)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM programs")
    rows = cursor.fetchall()

    conn.close()  # ✅ close connection

    # ✅ Convert to proper JSON
    data = [dict(row) for row in rows]

    return {
        "count": len(data),
        "programs": data
    }