import aiohttp
import io
import logging
import traceback
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Polygon
from io import BytesIO
from app.config import settings
from app.repository import spatial as spatial_repo # Import spatial repository
from sqlalchemy.ext.asyncio import AsyncSession # Import AsyncSession for type hint
from PIL import Image
from typing import Optional



logger = logging.getLogger(__name__)

async def upload_to_imgur(image_data: bytes, title: str = "Simple upload", description: str = "This is a simple image upload in Imgur") -> str | None:
    """Uploads image data to Imgur and returns the link, or None on failure."""
    headers = {'Authorization': f"Client-ID {settings.IMGUR_CLIENT_ID}"}
    try:
        # Ensure image is in JPEG format using Pillow
        img = Image.open(io.BytesIO(image_data))
        if img.format != 'JPEG':
            output = io.BytesIO()
            img = img.convert('RGB')
            img.save(output, format='JPEG', quality=85) # Added quality for PIL save
            image_data = output.getvalue()

        async with aiohttp.ClientSession() as session:
            form_data = aiohttp.FormData()
            form_data.add_field('image', image_data, content_type='image/jpeg')
            form_data.add_field('type', 'image')
            form_data.add_field('title', title)
            form_data.add_field('description', description)

            async with session.post('https://api.imgur.com/3/image', headers=headers, data=form_data) as response:
                response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
                data = await response.json()
                if data.get("success"):
                    return data.get("data", {}).get("link")
                else:
                    logger.error(f"Imgur upload failed: {data}")
                    return None
    except aiohttp.ClientResponseError as http_err:
        logger.error(f"HTTP error during Imgur upload: {http_err.status} - {http_err.message}")
    except Exception as e:
        logger.error(f"Error uploading to Imgur: {str(e)}\n{traceback.format_exc()}")
    return None # Return None if upload fails

def generate_polygon_image(coordinates: list, title: str = "Polygon Visualization") -> bytes | None:
    """Generates a JPEG image visualizing the polygon."""
    try:
        if not coordinates:
            return None

        polygon_geom = Polygon(coordinates)
        gdf = gpd.GeoDataFrame([1], geometry=[polygon_geom], crs="EPSG:4326")

        fig, ax = plt.subplots(figsize=(8, 8)) # Adjusted size slightly
        gdf.plot(ax=ax, edgecolor='black', facecolor='lightblue') # Simple styling

        # Set plot limits based on polygon bounds with some padding
        minx, miny, maxx, maxy = polygon_geom.bounds
        padding_x = (maxx - minx) * 0.1
        padding_y = (maxy - miny) * 0.1
        ax.set_xlim(minx - padding_x, maxx + padding_x)
        ax.set_ylim(miny - padding_y, maxy + padding_y)

        ax.set_title(title)
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        ax.set_aspect('equal', adjustable='box') # Ensure aspect ratio is correct

        buf = BytesIO()
        # Use dpi for better control over image resolution if needed
        fig.savefig(buf, format='jpeg', dpi=100)
        plt.close(fig) # Close the figure to free memory
        buf.seek(0)
        return buf.read()
    except Exception as e:
        logger.error(f"Error generating polygon image: {str(e)}\n{traceback.format_exc()}")
        return None

def generate_points_map_image(gdf: gpd.GeoDataFrame, title: str = "Map Image") -> bytes | None:
    """Generates a JPEG image visualizing points from a GeoDataFrame."""
    if gdf.empty:
        return None
    try:
        fig, ax = plt.subplots(figsize=(10, 10))
        gdf.plot(ax=ax, marker='o', color='blue', markersize=5)

        # Set plot limits based on points bounds with some padding
        minx, miny, maxx, maxy = gdf.total_bounds
        padding_x = (maxx - minx) * 0.1 if maxx > minx else 0.1
        padding_y = (maxy - miny) * 0.1 if maxy > miny else 0.1
        ax.set_xlim(minx - padding_x, maxx + padding_x)
        ax.set_ylim(miny - padding_y, maxy + padding_y)

        ax.set_title(title)
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        ax.set_aspect('equal', adjustable='box') # Try to keep aspect ratio

        buf = BytesIO()
        fig.savefig(buf, format='jpeg', dpi=150) # Increase DPI for potentially better quality
        plt.close(fig)
        buf.seek(0)
        return buf.read()
    except Exception as e:
        logger.error(f"Error generating points map image: {str(e)}\n{traceback.format_exc()}")
        return None

async def create_map_image_from_bbox(db: AsyncSession, bbox: tuple) -> Optional[str]:
    """Fetches points in bbox, generates image, uploads, returns URL or None."""
    gdf = await spatial_repo.get_points_in_bbox(db, bbox)
    if gdf.empty:
        logger.info(f"No data found in bbox {bbox} for image generation.")
        return None # Indicate no data found

    image_data = generate_points_map_image(gdf, title=f"Map for BBox: {bbox}")
    if not image_data:
        logger.error("Failed to generate map image from GeoDataFrame.")
        return None # Indicate image generation failed

    imgur_url = await upload_to_imgur(
        image_data,
        title="Map Image",
        description=f"Map generated for bbox: {bbox}"
    )

    if not imgur_url:
        logger.error("Failed to upload generated map image to Imgur.")
        # Optionally, you could save the image locally for debugging here
        return None # Indicate upload failed

    return imgur_url