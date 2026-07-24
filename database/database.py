import aiosqlite


DATABASE = "authorized_users.db"


async def initialize_database():
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY
            )
        """)

        await db.commit()


async def add_user(user_id):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
            (user_id,)
        )

        await db.commit()


async def remove_user(user_id):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute(
            "DELETE FROM users WHERE user_id = ?",
            (user_id,)
        )

        await db.commit()


async def is_authorized(user_id):
    async with aiosqlite.connect(DATABASE) as db:
        cursor = await db.execute(
            "SELECT user_id FROM users WHERE user_id = ?",
            (user_id,)
        )

        result = await cursor.fetchone()

        return result is not None

async def get_users():
    async with aiosqlite.connect(DATABASE) as db:
        cursor = await db.execute(
            "SELECT user_id FROM users"
        )

        rows = await cursor.fetchall()

        return [row[0] for row in rows]
