from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Geometry
from sqlalchemy.dialects.postgresql import JSONB

Base = declarative_base()

class PointDB(Base):
    """SQLAlchemy model for storing point geometry data"""
    __tablename__ = "points"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    geom = Column(Geometry("POINT", srid=4326), nullable=False)
    meta = Column(JSONB)
    
    def __repr__(self):
        return f"<Point {self.id}: {self.name}>"

class PolygonDB(Base):
    """SQLAlchemy model for storing polygon geometry data"""
    __tablename__ = "polygons"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    geom = Column(Geometry("POLYGON", srid=4326), nullable=False)
    meta = Column(JSONB)
    
    def __repr__(self):
        return f"<Polygon {self.id}: {self.name}>" 