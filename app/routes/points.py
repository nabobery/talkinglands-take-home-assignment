from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2.shape import to_shape
from typing import List, Optional
from app.schemas import PointCreate, PointResponse
from app.services import points as points_service
from app.db import get_db

router = APIRouter()

@router.post("/", response_model=PointResponse, status_code=201, summary="Create a new point")
async def create_point(
    point: PointCreate, 
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new point with the provided details:
    - **name**: Name or identifier for the point
    - **latitude**: Latitude coordinate (y)
    - **longitude**: Longitude coordinate (x)
    - **metadata**: Optional additional data about the point
    """
    db_point = await points_service.create_point(db, point)
    point_shape = to_shape(db_point.geom)
    return PointResponse(
        id=db_point.id,
        name=db_point.name,
        latitude=point_shape.y,
        longitude=point_shape.x,
        metadata=db_point.meta
    )

@router.get("/{point_id}", response_model=PointResponse, summary="Get a point by ID")
async def get_point(
    point_id: int, 
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a point by its ID
    """
    db_point = await points_service.get_point(db, point_id)
    if not db_point:
        raise HTTPException(status_code=404, detail="Point not found")
    
    point_shape = to_shape(db_point.geom)
    return PointResponse(
        id=db_point.id,
        name=db_point.name,
        latitude=point_shape.y,
        longitude=point_shape.x,
        metadata=db_point.meta
    )

@router.get("/", response_model=List[PointResponse], summary="Get all points")
async def get_all_points(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve all points with pagination
    """
    points = await points_service.get_all_points(db, skip, limit)
    return [
        PointResponse(
            id=point.id,
            name=point.name,
            latitude=to_shape(point.geom).y,
            longitude=to_shape(point.geom).x,
            metadata=point.meta
        ) for point in points
    ]

@router.put("/{point_id}", response_model=PointResponse, summary="Update a point")
async def update_point(
    point_id: int, 
    point: PointCreate, 
    db: AsyncSession = Depends(get_db)
):
    """
    Update a point with the provided details
    """
    db_point = await points_service.update_point(db, point_id, point)
    if not db_point:
        raise HTTPException(status_code=404, detail="Point not found")
    
    point_shape = to_shape(db_point.geom)
    return PointResponse(
        id=db_point.id,
        name=db_point.name,
        latitude=point_shape.y,
        longitude=point_shape.x,
        metadata=db_point.meta
    )

@router.delete("/{point_id}", status_code=204, summary="Delete a point")
async def delete_point(
    point_id: int, 
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a point by its ID
    """
    success = await points_service.delete_point(db, point_id)
    if not success:
        raise HTTPException(status_code=404, detail="Point not found")
    return None 