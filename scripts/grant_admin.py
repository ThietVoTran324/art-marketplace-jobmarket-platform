"""Grant the admin role to an existing user (local manual testing helper).

Usage (inside the fastapi container):
    python scripts/grant_admin.py <username>
"""
import asyncio
import sys

from sqlalchemy import text

from app.postgresql.database import async_session_maker


async def main(username: str) -> None:
    async with async_session_maker() as session:
        user_id = await session.scalar(
            text("SELECT id FROM users WHERE username = :username"), {"username": username}
        )
        if user_id is None:
            print(f"user not found: {username}")
            raise SystemExit(1)

        await session.execute(
            text(
                "INSERT INTO user_roles (user_id, role) VALUES (:uid, 'admin') "
                "ON CONFLICT DO NOTHING"
            ),
            {"uid": user_id},
        )
        await session.commit()

        roles = (
            await session.execute(
                text("SELECT role FROM user_roles WHERE user_id = :uid ORDER BY role"),
                {"uid": user_id},
            )
        ).scalars()
        print(f"user_id={user_id} username={username} roles={list(roles)}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python scripts/grant_admin.py <username>")
        raise SystemExit(2)
    asyncio.run(main(sys.argv[1]))
