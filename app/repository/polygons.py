from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from geoalchemy2.shape import from_shape
from shapely.geometry import Polygon
from app.models import PolygonDB
from app.schemas import PolygonCreate

async def create_polygon(db: AsyncSession, polygon: PolygonCreate) -> PolygonDB:
    """Create a new polygon in the database"""
    geom = Polygon(polygon.coordinates)
    db_polygon = PolygonDB(
        name=polygon.name,
        geom=from_shape(geom, srid=4326),
        meta=polygon.metadata
    )
    db.add(db_polygon)
    await db.commit()
    await db.refresh(db_polygon)
    return db_polygon

async def get_polygon(db: AsyncSession, polygon_id: int) -> PolygonDB:
    """Get a polygon by ID"""
    result = await db.execute(select(PolygonDB).filter(PolygonDB.id == polygon_id))
    return result.scalars().first()

async def get_all_polygons(db: AsyncSession, skip: int = 0, limit: int = 100):
    """Get all polygons with pagination"""
    result = await db.execute(select(PolygonDB).offset(skip).limit(limit))
    return result.scalars().all()

async def update_polygon(db: AsyncSession, polygon_id: int, polygon: PolygonCreate) -> PolygonDB:
    """Update a polygon by ID"""
    result = await db.execute(select(PolygonDB).filter(PolygonDB.id == polygon_id))
    db_polygon = result.scalars().first()
    if not db_polygon:
        return None
        
    geom = Polygon(polygon.coordinates)
    db_polygon.name = polygon.name
    db_polygon.geom = from_shape(geom, srid=4326)
    db_polygon.meta = polygon.metadata
    
    await db.commit()
    await db.refresh(db_polygon)
    return db_polygon

async def delete_polygon(db: AsyncSession, polygon_id: int) -> bool:
    """Delete a polygon by ID"""
    result = await db.execute(select(PolygonDB).filter(PolygonDB.id == polygon_id))
    db_polygon = result.scalars().first()
    if not db_polygon:
        return False
        
    await db.delete(db_polygon)
    await db.commit()
    return True 