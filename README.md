# Talking Lands Take Home Assignment

## Spatial Data Platform API

A backend API for storing, retrieving, and querying spatial datasets, built with FastAPI and PostgreSQL/PostGIS.

## Features

- Store, update, and retrieve point data
- Store, update, and retrieve polygon data
- Perform spatial queries:
  - Find points within a polygon
  - Find points within a radius of a reference point
  - Find polygons containing a point
  - Find overlapping polygons
  - Generate map image from spatial data and get Imgur URL

## Tech Stack

- **Python**: Core language
- **FastAPI**: API framework
- **PostgreSQL + PostGIS**: Spatial database
- **SQLAlchemy + GeoAlchemy2**: ORM with spatial extension
- **asyncpg**: Async PostgreSQL driver
- **Shapely**: Python library for manipulation and analysis of geometric objects
- **matplotlib & geopandas**: For generating map images
- **aiohttp**: For async HTTP requests (Imgur upload)

## Project Structure

```bash
talkinglands-take-home-assignment/
├── main.py                 # Main application entry point
├── requirements.txt        # Dependencies
└── app/                    # Application package
    ├── config.py           # Configuration settings
    ├── db.py               # Database setup
    ├── models.py           # SQLAlchemy models
    ├── schemas.py          # Pydantic schemas
    ├── repository/         # Database operations
    │   ├── points.py       # Point CRUD operations
    │   ├── polygons.py     # Polygon CRUD operations
    │   └── spatial.py      # Spatial queries (including get_points_in_bbox)
    ├── services/           # Business logic
    │   ├── points.py       # Point services
    │   ├── polygons.py     # Polygon services (handles polygon image generation/upload)
    │   ├── spatial.py      # Spatial services
    │   └── image_service.py # Image generation & Imgur upload logic
    └── routes/             # API endpoints
        ├── points.py       # Point routes
        ├── polygons.py     # Polygon routes (returns image_url)
        ├── spatial.py      # Endpoints for spatial queries
        └── generate_map_image.py  # Endpoint to generate map image from bbox
```

## Setup Instructions

1. **Install PostgreSQL and PostGIS**

   Follow the [PostgreSQL installation instructions](https://www.postgresql.org/download/) for your operating system.

   Enable PostGIS in your database:

   ```sql
   CREATE DATABASE spatial_platform;
   \c spatial_platform
   CREATE EXTENSION postgis;
   ```

2. **Configure Database Connection**

   Update the `.env` file in the project root with your PostgreSQL and Imgur Client ID credentials:

   ```env
   DATABASE_URL="postgresql+asyncpg://username:password@localhost:5432/spatial_platform"
   IMGUR_CLIENT_ID="YOUR_IMGUR_CLIENT_ID" # Replace with your Imgur Client ID
   ```

3. **Install Python Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**

   ```bash
   python main.py
   ```

   The API will be available at <http://localhost:8000>.
   Interactive API documentation is available at <http://localhost:8000/docs>.

## API Endpoints

### Points

- `POST /points/`: Create a new point
- `GET /points/`: Get all points (with pagination)
- `GET /points/{point_id}`: Get a point by ID
- `PUT /points/{point_id}`: Update a point
- `DELETE /points/{point_id}`: Delete a point

### Polygons

- `POST /polygons/`: Create a new polygon
- `GET /polygons/`: Get all polygons (with pagination)
- `GET /polygons/{polygon_id}`: Get a polygon by ID
- `PUT /polygons/{polygon_id}`: Update a polygon
- `DELETE /polygons/{polygon_id}`: Delete a polygon

### Spatial Queries

- `GET /spatial/points-in-polygon/{polygon_id}`: Get all points within a polygon
- `GET /spatial/points-near/{point_id}/{radius}`: Get all points within a radius of a point
- `GET /spatial/polygons-containing-point/{point_id}`: Get all polygons containing a point
- `GET /spatial/overlapping-polygons/{polygon_id}`: Get all polygons that overlap with a polygon

### Images

- `GET /images/generate-map-image`: Generate map image from points in a bounding box and get Imgur URL

## Example Usage

### Points API Examples

#### Create a Point

```bash
curl -X POST "http://localhost:8000/points/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Coffee Shop",
    "latitude": 34.0522,
    "longitude": -118.2437,
    "meta": {
      "amenity": "cafe",
      "wifi": true
    }
  }'
```

#### Get a Point by ID

```bash
curl "http://localhost:8000/points/1"
```

#### Get All Points (Paginated)

```bash
curl "http://localhost:8000/points/?skip=0&limit=10"
```

#### Update a Point

```bash
curl -X PUT "http://localhost:8000/points/1" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Coffee Shop",
    "latitude": 34.0523,
    "longitude": -118.2438,
    "meta": {
      "amenity": "cafe",
      "wifi": false,
      "updated": true
    }
  }'
```

#### Delete a Point

```bash
curl -X DELETE "http://localhost:8000/points/1"
```

### Polygons API Examples

#### Create a Polygon

```bash
curl -X POST "http://localhost:8000/polygons/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "City Park",
    "coordinates": [
      [ -118.244, 34.053 ],
      [ -118.244, 34.054 ],
      [ -118.245, 34.054 ],
      [ -118.245, 34.053 ],
      [ -118.244, 34.053 ]
    ],
    "meta": {
      "type": "park",
      "area": "large"
    }
  }'
```

#### Get a Polygon by ID

```bash
curl "http://localhost:8000/polygons/1"
```

#### Get All Polygons (Paginated)

```bash
curl "http://localhost:8000/polygons/?skip=0&limit=10"
```

#### Update a Polygon

```bash
curl -X PUT "http://localhost:8000/polygons/1" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated City Park",
    "coordinates": [
      [ -118.243, 34.052 ],
      [ -118.243, 34.053 ],
      [ -118.244, 34.053 ],
      [ -118.244, 34.052 ],
      [ -118.243, 34.052 ]
    ],
    "meta": {
      "type": "park",
      "area": "medium",
      "updated": true
    }
  }'
```

#### Delete a Polygon

```bash
curl -X DELETE "http://localhost:8000/polygons/1"
```

### Spatial Query Examples

#### Get Points within a Polygon

(Assuming polygon with ID 1 exists)

```bash
curl "http://localhost:8000/spatial/points-in-polygon/1"
```

#### Get Points near a Point (within 1000 meters radius)

(Assuming point with ID 1 exists)

```bash
curl "http://localhost:8000/spatial/points-near/1/1000"
```

#### Get Polygons containing a Point

(Assuming point with ID 1 exists)

```bash
curl "http://localhost:8000/spatial/polygons-containing-point/1"
```

#### Get Overlapping Polygons

Assuming polygon with ID 1 exists

```bash
curl "http://localhost:8000/spatial/overlapping-polygons/1"
```

### Image Generation Example

#### Generate Map Image for a Bounding Box

```bash
curl "http://localhost:8000/images/generate-map-image?min_lat=34.0&max_lat=34.1&min_lon=-118.3&max_lon=-118.2"
```

## Response (Example)

```json
{
  "image_url": "https://i.imgur.com/..."
}
```

## License

This project is licensed under the MIT License.
