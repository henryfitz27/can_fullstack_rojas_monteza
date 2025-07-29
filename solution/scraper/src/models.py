from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from .settings import Base
from datetime import datetime

class File(Base):
    """
    Modelo para la tabla files
    """
    __tablename__ = "files"
    
    id = Column("id", Integer, primary_key=True, index=True)
    total_links = Column(Integer, nullable=False)
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    total_processed = Column(Integer, nullable=False, default=0)
    total_failed = Column(Integer, nullable=False, default=0)
    status = Column(String(50), nullable=False)
    uploaded_at = Column(DateTime, nullable=False)
    user_id = Column(Integer, nullable=False)
    
    # Relación uno a muchos con Link
    links = relationship("Link", back_populates="file", cascade="all, delete-orphan")

class Link(Base):
    """
    Modelo para la tabla links
    """
    __tablename__ = "links"
    
    id = Column("id", Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("files.id"), nullable=False)
    url = Column(String(2000), nullable=False)
    title = Column(String(500), nullable=True)
    post_date = Column(DateTime, nullable=True)
    content = Column(Text, nullable=True)
    page_exists = Column(Boolean, nullable=False, default=False)
    success = Column(Boolean, nullable=False, default=False)
    error_description = Column(String(1000), nullable=True)
    processed_date = Column(DateTime, nullable=True, default=datetime.utcnow)
    
    # Relación muchos a uno con File
    file = relationship("File", back_populates="links")