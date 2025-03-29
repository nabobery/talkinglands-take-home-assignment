from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routes import points, polygons, spatial, generate_map_image
from app.models import Base
from app.db import engine
from mangum import Mangum

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(
    lifespan=lifespan,
    title="Spatial Data Platform API",
    description="API for storing, retrieving, and querying spatial data",
    version="1.0.0"
)

app.include_router(points.router, prefix="/points", tags=["Points"])
app.include_router(polygons.router, prefix="/polygons", tags=["Polygons"])
app.include_router(spatial.router, prefix="/spatial", tags=["Spatial"])
app.include_router(generate_map_image.router, prefix="/images", tags=["Images"])

handler = Mangum(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("functions.main:app", host="0.0.0.0", port=8000, reload=True) 