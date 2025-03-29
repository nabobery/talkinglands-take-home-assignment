from sqlalchemy.ext.asyncio import AsyncSession
from app.repository import spatial as spatial_repo

async def get_points_in_polygon(db: AsyncSession, polygon_id: int):
    """Service function to get all points within a polygon"""
    return await spatial_repo.get_points_in_polygon(db, polygon_id)

async def get_points_near(db: AsyncSession, point_id: int, radius_meters: float):
    """Service function to get all points within a radius of another point"""
    return await spatial_repo.get_points_near(db, point_id, radius_meters)

async def get_polygons_containing_point(db: AsyncSession, point_id: int):
    """Service function to get all polygons containing a point"""
    return await spatial_repo.get_polygons_containing_point(db, point_id)

async def get_overlapping_polygons(db: AsyncSession, polygon_id: int):
    """Service function to get all polygons that overlap with a polygon"""
    return await spatial_repo.get_overlapping_polygons(db, polygon_id) 