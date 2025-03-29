from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.services import image_service # Import the image service
from app.db import get_db
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/generate-map-image", response_model=dict)
async def generate_map_image_endpoint(
    min_lat: float = Query(..., description="Minimum latitude"),
    max_lat: float = Query(..., description="Maximum latitude"),
    min_lon: float = Query(..., description="Minimum longitude"),
    max_lon: float = Query(..., description="Maximum longitude"),
    db: AsyncSession = Depends(get_db) # Use AsyncSession type hint
):
    """
    Generates a map image based on points within the specified bounding box,
    uploads it to Imgur, and returns the image URL.
    """
    bbox = (min_lon, min_lat, max_lon, max_lat)
    try:
        # Call the coordinating service function
        image_url = await image_service.create_map_image_from_bbox(db, bbox)

        if image_url is None:
            # Decide how to respond if no data or failure
            # Option 1: 404 if no data (maybe check gdf.empty status returned from service?)
            # Option 2: 500 if generation/upload failed
            # For now, let's assume 404 if url is None, implying no data or failure upstream
             raise HTTPException(status_code=404, detail="Could not generate or upload image. No data found or error occurred.")

        return {"image_url": image_url}

    except HTTPException as http_exc:
        # Re-raise HTTPExceptions (like the 404 above)
        raise http_exc
    except Exception as e:
        logger.error(f"Unexpected error in generate_map_image_endpoint: {str(e)}", exc_info=True)
        # Catch any other unexpected errors
        raise HTTPException(status_code=500, detail="Internal server error while processing the image.")