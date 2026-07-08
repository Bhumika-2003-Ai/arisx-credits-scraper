import sqlite3

def get_connection():
    return sqlite3.connect("credits.db")


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS programs (
        provider TEXT,
        program TEXT,
        credits TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_to_db(programs):
    conn = get_connection()
    cursor = conn.cursor()

    for p in programs:
        cursor.execute(
            "INSERT INTO programs VALUES (?, ?, ?)",
            (
                p.provider,
                p.program_name,
                p.credit_amount
            )
        )

    conn.commit()
    conn.close()

    print("✓ Data saved to DB")