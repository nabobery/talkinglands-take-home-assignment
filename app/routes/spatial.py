from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2.shape import to_shape
from typing import List, Optional
from app.schemas import PointResponse, PolygonResponse
from app.services import spatial as spatial_service
from app.db import get_db

router = APIRouter()

@router.get(
    "/points-in-polygon/{polygon_id}", 
    response_model=List[PointResponse],
    summary="Find all points within a polygon"
)
async def get_points_in_polygon(
    polygon_id: int = Path(..., description="The ID of the polygon"), 
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve all points that are located within the specified polygon.
    
    This is a spatial query that uses the PostGIS ST_Within function to find
    points whose geometries are completely inside the polygon.
    """
    points = await spatial_service.get_points_in_polygon(db, polygon_id)
    if points is None:
        raise HTTPException(status_code=404, detail="Polygon not found")
        
    return [
        PointResponse(
            id=point.id,
            name=point.name,
            latitude=to_shape(point.geom).y,
            longitude=to_shape(point.geom).x,
            metadata=point.metadata
        ) for point in points
    ]

@router.get(
    "/points-near/{point_id}/{radius}", 
    response_model=List[PointResponse],
    summary="Find all points within a radius"
)
async def get_points_near(
    point_id: int = Path(..., description="The ID of the reference point"),
    radius: float = Path(..., description="The radius in meters"),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve all points that are within a specified radius of the reference point.
    
    This spatial query uses the PostGIS ST_DWithin function with a geography cast
    to find points within the given distance in meters.
    """
    points = await spatial_service.get_points_near(db, point_id, radius)
    if points is None:
        raise HTTPException(status_code=404, detail="Reference point not found")
        
    return [
        PointResponse(
            id=point.id,
            name=point.name,
            latitude=to_shape(point.geom).y,
            longitude=to_shape(point.geom).x,
            metadata=point.meta
        ) for point in points
    ]

@router.get(
    "/polygons-containing-point/{point_id}", 
    response_model=List[PolygonResponse],
    summary="Find all polygons containing a point"
)
async def get_polygons_containing_point(
    point_id: int = Path(..., description="The ID of the point"), 
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve all polygons that contain the specified point.
    
    This spatial query uses the PostGIS ST_Contains function to find
    polygons whose geometries completely contain the point.
    """
    polygons = await spatial_service.get_polygons_containing_point(db, point_id)
    if polygons is None:
        raise HTTPException(status_code=404, detail="Point not found")
        
    return [
        PolygonResponse(
            id=polygon.id,
            name=polygon.name,
            coordinates=list(to_shape(polygon.geom).exterior.coords),
            metadata=polygon.metadata
        ) for polygon in polygons
    ]

@router.get(
    "/overlapping-polygons/{polygon_id}", 
    response_model=List[PolygonResponse],
    summary="Find all polygons overlapping with a polygon"
)
async def get_overlapping_polygons(
    polygon_id: int = Path(..., description="The ID of the reference polygon"), 
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve all polygons that overlap with the specified polygon.
    
    This spatial query uses the PostGIS ST_Overlaps function to find
    polygons whose geometries share some portion of space with the reference
    polygon without being completely inside or containing it.
    """
    polygons = await spatial_service.get_overlapping_polygons(db, polygon_id)
    if polygons is None:
        raise HTTPException(status_code=404, detail="Reference polygon not found")
        
    return [
        PolygonResponse(
            id=polygon.id,
            name=polygon.name,
            coordinates=list(to_shape(polygon.geom).exterior.coords),
            metadata=polygon.metadata
        ) for polygon in polygons
    ] 