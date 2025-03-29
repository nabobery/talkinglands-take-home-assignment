from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2.shape import to_shape
from typing import List, Optional
from app.schemas import PolygonCreate, PolygonResponse
from app.services import polygons as polygons_service
from app.db import get_db

router = APIRouter()

@router.post("/", response_model=PolygonResponse, status_code=201, summary="Create a new polygon")
async def create_polygon(
    polygon: PolygonCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new polygon with the provided details:
    - **name**: Name or identifier for the polygon
    - **coordinates**: List of [longitude, latitude] pairs forming the polygon
    - **meta**: Optional additional data about the polygon
    """
    db_polygon, image_url = await polygons_service.create_polygon(db, polygon)
    if not db_polygon:
         # Handle case where polygon creation might fail in repo (though unlikely with current repo code)
         raise HTTPException(status_code=500, detail="Failed to create polygon")

    polygon_shape = to_shape(db_polygon.geom)
    return PolygonResponse(
        id=db_polygon.id,
        name=db_polygon.name,
        coordinates=list(polygon_shape.exterior.coords),
        metadata=db_polygon.meta,
        image_url=image_url # Include the image URL
    )

@router.get("/{polygon_id}", response_model=PolygonResponse, summary="Get a polygon by ID")
async def get_polygon(
    polygon_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a polygon by its ID
    """
    db_polygon, image_url = await polygons_service.get_polygon(db, polygon_id)
    if not db_polygon:
        raise HTTPException(status_code=404, detail="Polygon not found")

    polygon_shape = to_shape(db_polygon.geom)
    return PolygonResponse(
        id=db_polygon.id,
        name=db_polygon.name,
        coordinates=list(polygon_shape.exterior.coords),
        metadata=db_polygon.meta,
        image_url=image_url # Include the image URL
    )

@router.get("/", response_model=List[PolygonResponse], summary="Get all polygons")
async def get_all_polygons(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve all polygons with pagination.
    NOTE: Image URLs are not generated for this list endpoint for performance.
    Request individual polygons to get their image URLs.
    """
    polygons = await polygons_service.get_all_polygons(db, skip, limit)
    return [
        PolygonResponse(
            id=polygon.id,
            name=polygon.name,
            coordinates=list(to_shape(polygon.geom).exterior.coords),
            metadata=polygon.meta,
            image_url=None # Explicitly None for the list view
        ) for polygon in polygons
    ]

@router.put("/{polygon_id}", response_model=PolygonResponse, summary="Update a polygon")
async def update_polygon(
    polygon_id: int,
    polygon: PolygonCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a polygon with the provided details
    """
    db_polygon, image_url = await polygons_service.update_polygon(db, polygon_id, polygon)
    if not db_polygon:
        raise HTTPException(status_code=404, detail="Polygon not found")

    polygon_shape = to_shape(db_polygon.geom)
    return PolygonResponse(
        id=db_polygon.id,
        name=db_polygon.name,
        coordinates=list(polygon_shape.exterior.coords),
        metadata=db_polygon.meta,
        image_url=image_url # Include the image URL
    )

@router.delete("/{polygon_id}", status_code=204, summary="Delete a polygon")
async def delete_polygon(
    polygon_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a polygon by its ID
    """
    success = await polygons_service.delete_polygon(db, polygon_id)
    if not success:
        raise HTTPException(status_code=404, detail="Polygon not found")
    return None # No content response 