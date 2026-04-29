from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from database.bootstrap import bootstrap_auth_data
from database.session_postgresql import AsyncPostgresqlSessionLocal
from routes import (
    accounts_router,
    profiles_router,
    movies_router,
    genres_router,
    stars_router,
    directors_router,
)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    async with AsyncPostgresqlSessionLocal() as session:
        await bootstrap_auth_data(session=session)
        await session.commit()
    yield


app = FastAPI(
    title="Online Cinema",
    description="Modern and user-friendly API for Online Cinema project",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "accounts",
            "description": "Authentication, account lifecycle and roles.",
        },
        {"name": "profiles", "description": "User profile creation and media upload."},
        {
            "name": "movies",
            "description": "Movie catalog, ratings, votes, comments and favorites.",
        },
        {"name": "genres", "description": "Genre management and analytics."},
        {"name": "stars", "description": "Movie stars management."},
        {"name": "directors", "description": "Movie directors management."},
    ],
    lifespan=lifespan,
)

app.include_router(accounts_router, prefix="/accounts", tags=["accounts"])
app.include_router(profiles_router, prefix="/profiles", tags=["profiles"])
app.include_router(movies_router, prefix="/theater", tags=["movies"])
app.include_router(genres_router, prefix="/theater/genres", tags=["genres"])
app.include_router(stars_router, prefix="/theater/stars", tags=["stars"])
app.include_router(directors_router, prefix="/theater/directors", tags=["directors"])
