from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class PointCreate(BaseModel):
    """Schema for creating a point"""
    name: str
    latitude: float = Field(..., description="Latitude coordinate (y)")
    longitude: float = Field(..., description="Longitude coordinate (x)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional data about the point")

class PolygonCreate(BaseModel):
    """Schema for creating a polygon"""
    name: str
    coordinates: List[List[float]] = Field(..., description="List of [longitude, latitude] pairs forming a polygon")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional data about the polygon")

class PointResponse(BaseModel):
    """Schema for point response"""
    id: int
    name: str
    latitude: float
    longitude: float
    metadata: Optional[Dict[str, Any]]
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Black Cat",
                "latitude": 38.9146,
                "longitude": -77.0317,
                "metadata": {
                    "event": "Muhsinah plays tonight",
                    "time": "9:00 p.m.",
                    "price": "$12"
                }
            }
        }

class PolygonResponse(BaseModel):
    """Schema for polygon response"""
    id: int
    name: str
    coordinates: List[List[float]]
    metadata: Optional[Dict[str, Any]]
    image_url: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Arlington",
                "coordinates": [
                    [-77.1, 38.9],
                    [-77.1, 38.8],
                    [-77.0, 38.8],
                    [-77.0, 38.9],
                    [-77.1, 38.9]
                ],
                "metadata": {
                    "population_density": 238000
                },
                "image_url": "https://i.imgur.com/..."
            }
        }
        from_attributes = True 