import asyncio

import aiopg

dsn = "dbname=XXX user=XXX password=XXX host=127.0.0.1"  # change me


async def listen(conn):
    async with conn.cursor() as cur:
        await cur.execute("LISTEN events")
        while True:
            msg = await conn.notifies.get()
            print("Receive <-", msg.payload)


async def main():
    async with aiopg.create_pool(dsn) as pool:
        async with pool.acquire() as conn1:
            listener = listen(conn1)
            await listener


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
