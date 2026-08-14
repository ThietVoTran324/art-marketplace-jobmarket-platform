import asyncio

from sqlalchemy import text

from app.postgresql.database import async_session_maker


async def main():
    async with async_session_maker() as s:
        users = await s.scalar(text("select count(*) from users"))
        roles = (await s.execute(text("select role, count(*) from user_roles group by role order by role"))).all()
        admins = (
            await s.execute(
                text(
                    "select u.username from users u "
                    "join user_roles r on r.user_id=u.id where r.role='admin'"
                )
            )
        ).all()
        print("users", users)
        print("roles", roles)
        print("admins", [r[0] for r in admins])


if __name__ == "__main__":
    asyncio.run(main())
