from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2.shape import to_shape
from app.repository import polygons as polygons_repo
from app.schemas import PolygonCreate
from app.models import PolygonDB
from app.services import image_service
from typing import Tuple, Optional, List

async def create_polygon(db: AsyncSession, polygon: PolygonCreate) -> Tuple[PolygonDB, Optional[str]]:
    """Creates a polygon, generates/uploads image, returns polygon object and image URL."""
    db_polygon = await polygons_repo.create_polygon(db, polygon)
    image_url = None
    if db_polygon:
        polygon_shape = to_shape(db_polygon.geom)
        image_data = image_service.generate_polygon_image(list(polygon_shape.exterior.coords), db_polygon.name)
        if image_data:
            image_url = await image_service.upload_to_imgur(
                image_data,
                title=f"Polygon: {db_polygon.name} (ID: {db_polygon.id})",
                description=f"Visualization of polygon {db_polygon.name}"
            )
    return db_polygon, image_url

async def get_polygon(db: AsyncSession, polygon_id: int) -> Tuple[Optional[PolygonDB], Optional[str]]:
    """Gets a polygon by ID, generates/uploads image, returns polygon object and image URL."""
    db_polygon = await polygons_repo.get_polygon(db, polygon_id)
    image_url = None
    if db_polygon:
        polygon_shape = to_shape(db_polygon.geom)
        image_data = image_service.generate_polygon_image(list(polygon_shape.exterior.coords), db_polygon.name)
        if image_data:
            image_url = await image_service.upload_to_imgur(
                image_data,
                title=f"Polygon: {db_polygon.name} (ID: {db_polygon.id})",
                description=f"Visualization of polygon {db_polygon.name}"
            )
    return db_polygon, image_url

async def get_all_polygons(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[PolygonDB]:
    """Gets all polygons with pagination (no image generation for list)."""
    # No image generation here for performance reasons
    return await polygons_repo.get_all_polygons(db, skip, limit)

async def update_polygon(db: AsyncSession, polygon_id: int, polygon: PolygonCreate) -> Tuple[Optional[PolygonDB], Optional[str]]:
    """Updates a polygon, generates/uploads image, returns updated polygon object and image URL."""
    db_polygon = await polygons_repo.update_polygon(db, polygon_id, polygon)
    image_url = None
    if db_polygon:
        polygon_shape = to_shape(db_polygon.geom)
        image_data = image_service.generate_polygon_image(list(polygon_shape.exterior.coords), db_polygon.name)
        if image_data:
            image_url = await image_service.upload_to_imgur(
                image_data,
                title=f"Polygon: {db_polygon.name} (ID: {db_polygon.id})",
                description=f"Visualization of polygon {db_polygon.name}"
            )
    return db_polygon, image_url

async def delete_polygon(db: AsyncSession, polygon_id: int) -> bool:
    """Deletes a polygon."""
    # No image generation needed for delete
    return await polygons_repo.delete_polygon(db, polygon_id) 