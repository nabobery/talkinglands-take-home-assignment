from sqlalchemy.ext.asyncio import AsyncSession
from app.repository import points as points_repo
from app.schemas import PointCreate
from typing import List, Optional

async def create_point(db: AsyncSession, point: PointCreate):
    """Service function to create a new point"""
    return await points_repo.create_point(db, point)

async def get_point(db: AsyncSession, point_id: int):
    """Service function to get a point by ID"""
    return await points_repo.get_point(db, point_id)

async def get_all_points(db: AsyncSession, skip: int = 0, limit: int = 100):
    """Service function to get all points with pagination"""
    return await points_repo.get_all_points(db, skip, limit)

async def update_point(db: AsyncSession, point_id: int, point: PointCreate):
    """Service function to update a point"""
    return await points_repo.update_point(db, point_id, point)

async def delete_point(db: AsyncSession, point_id: int):
    """Service function to delete a point"""
    return await points_repo.delete_point(db, point_id) 