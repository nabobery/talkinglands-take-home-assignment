from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, cast
from geoalchemy2.types import Geography
from geoalchemy2.shape import to_shape
from shapely.geometry import Point as ShapelyPoint # Renamed to avoid conflict
import geopandas as gpd
from app.models import PointDB, PolygonDB

async def get_points_in_polygon(db: AsyncSession, polygon_id: int):
    """Get all points that are within a specific polygon"""
    # First get the polygon
    polygon_result = await db.execute(select(PolygonDB).filter(PolygonDB.id == polygon_id))
    polygon = polygon_result.scalars().first()
    if not polygon:
        return None
    
    # Then find all points within that polygon using ST_Within
    query = select(PointDB).filter(func.ST_Within(PointDB.geom, polygon.geom))
    result = await db.execute(query)
    return result.scalars().all()

async def get_points_near(db: AsyncSession, point_id: int, radius_meters: float):
    """Get all points within a certain radius of a point"""
    # First get the reference point
    point_result = await db.execute(select(PointDB).filter(PointDB.id == point_id))
    reference_point = point_result.scalars().first()
    if not reference_point:
        return None
    
    # Then find all points within the specified radius using ST_DWithin
    # Note: ST_DWithin uses the units of the spatial reference system
    # For SRID 4326 (WGS84), we need to convert meters to degrees by casting to geography
    query = select(PointDB).filter(
        func.ST_DWithin(
            cast(func.ST_Transform(PointDB.geom, 4326), Geography),
            cast(func.ST_Transform(reference_point.geom, 4326), Geography),
            radius_meters
        )
    ).filter(PointDB.id != point_id)  # Exclude the reference point
    
    result = await db.execute(query)
    return result.scalars().all()

async def get_polygons_containing_point(db: AsyncSession, point_id: int):
    """Get all polygons that contain a specific point"""
    # First get the point
    point_result = await db.execute(select(PointDB).filter(PointDB.id == point_id))
    point = point_result.scalars().first()
    if not point:
        return None
    
    # Then find all polygons containing that point using ST_Contains
    query = select(PolygonDB).filter(func.ST_Contains(PolygonDB.geom, point.geom))
    result = await db.execute(query)
    return result.scalars().all()

async def get_overlapping_polygons(db: AsyncSession, polygon_id: int):
    """Get all polygons that overlap with a specific polygon"""
    # First get the reference polygon
    polygon_result = await db.execute(select(PolygonDB).filter(PolygonDB.id == polygon_id))
    reference_polygon = polygon_result.scalars().first()
    if not reference_polygon:
        return None
    
    # Then find all polygons that overlap with it using ST_Overlaps
    query = select(PolygonDB).filter(
        func.ST_Overlaps(PolygonDB.geom, reference_polygon.geom)
    ).filter(PolygonDB.id != polygon_id)  # Exclude the reference polygon
    
    result = await db.execute(query)
    return result.scalars().all()

async def get_points_in_bbox(db: AsyncSession, bbox: tuple) -> gpd.GeoDataFrame:
    """Get points within a bounding box and return as a GeoDataFrame."""
    min_lon, min_lat, max_lon, max_lat = bbox
    stmt = select(PointDB).filter(
        func.ST_Within(PointDB.geom, func.ST_MakeEnvelope(min_lon, min_lat, max_lon, max_lat, 4326))
    )
    result = await db.execute(stmt)
    points = result.scalars().all()

    if not points:
        return gpd.GeoDataFrame(geometry=[], crs="EPSG:4326") # Ensure empty gdf has correct structure

    geometries = [to_shape(p.geom) for p in points] # Use shapely geometries directly
    gdf = gpd.GeoDataFrame(
        [{"id": p.id, "name": p.name} for p in points], # Include name or other relevant data
        geometry=geometries,
        crs="EPSG:4326"
    )
    return gdf 