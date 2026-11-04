import aiosqlite

DB_NAME = "paymobile.db"

async def create_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                uc_amount INTEGER,
                price INTEGER,
                pubg_id TEXT,
                nickname TEXT,
                receipt TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()


async def save_order(
    user_id,
    username,
    uc_amount,
    price,
    pubg_id,
    nickname,
    receipt
):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            INSERT INTO orders (
                user_id, username, uc_amount,
                price, pubg_id, nickname, receipt
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            username,
            uc_amount,
            price,
            pubg_id,
            nickname,
            receipt
        ))

        await db.commit()
        return cursor.lastrowid


async def update_order(order_id, status):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            UPDATE orders
            SET status = ?
            WHERE id = ?
        """, (status, order_id))

        await db.commit()
