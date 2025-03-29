from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from app.models import PointDB
from app.schemas import PointCreate

async def create_point(db: AsyncSession, point: PointCreate) -> PointDB:
    """Create a new point in the database"""
    geom = Point(point.longitude, point.latitude)
    db_point = PointDB(
        name=point.name,
        geom=from_shape(geom, srid=4326),
        meta=point.metadata
    )
    db.add(db_point)
    await db.commit()
    await db.refresh(db_point)
    return db_point

async def get_point(db: AsyncSession, point_id: int) -> PointDB:
    """Get a point by ID"""
    result = await db.execute(select(PointDB).filter(PointDB.id == point_id))
    return result.scalars().first()

async def get_all_points(db: AsyncSession, skip: int = 0, limit: int = 100):
    """Get all points with pagination"""
    result = await db.execute(select(PointDB).offset(skip).limit(limit))
    return result.scalars().all()

async def update_point(db: AsyncSession, point_id: int, point: PointCreate) -> PointDB:
    """Update a point by ID"""
    result = await db.execute(select(PointDB).filter(PointDB.id == point_id))
    db_point = result.scalars().first()
    if db_point is None:
        return None
    
    geom = Point(point.longitude, point.latitude)
    db_point.name = point.name
    db_point.geom = from_shape(geom, srid=4326)
    db_point.meta = point.metadata
    
    await db.commit()
    await db.refresh(db_point)
    return db_point

async def delete_point(db: AsyncSession, point_id: int) -> bool:
    """Delete a point by ID"""
    result = await db.execute(select(PointDB).filter(PointDB.id == point_id))
    db_point = result.scalars().first()
    if not db_point:
        return False
        
    await db.delete(db_point)
    await db.commit()
    return True 