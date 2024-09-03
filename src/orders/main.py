import asyncio

import aiopg

dsn = "dbname=XXX user=XXX password=XXX host=127.0.0.1"  # change this to your actual database credentials


async def listen(conn):
    async with conn.cursor() as cur:
        await cur.execute("LISTEN events")
        while True:
            msg = await conn.notifies.get()
            print("Received:", msg.payload)


async def main(dsn=None):
    if not dsn:
        dsn = "dbname=XXX user=XXX password=XXX host=127.0.0.1"  # default value or environment variable
    async with aiopg.create_pool(dsn) as pool:
        async with pool.acquire() as conn:
            listener = listen(conn)
            await listener


if __name__ == "__main__":
    asyncio.run(main())
