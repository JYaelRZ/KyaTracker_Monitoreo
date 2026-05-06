from sqlalchemy import Column, String, Float, Integer, DateTime
from datetime import datetime, timezone
from database.connection import Base

class MonitoringService(Base):
    """Modelo para los servicios de Monitoreo Logístico"""
    __tablename__ = "monitoring_services"
    
    id = Column(String(36), primary_key=True) # UUID string
    unit = Column(String(100), nullable=False)
    operator = Column(String(150), nullable=False)
    client = Column(String(150), nullable=False)
    origin = Column(String(200), nullable=False)
    destination = Column(String(200), nullable=False)
    
    # Manejo de tiempos
    start_time = Column(DateTime(timezone=True), nullable=False)
    arrival_time = Column(DateTime(timezone=True), nullable=True)
    
    # Lógica financiera
    hourly_rate = Column(Float, nullable=False)
    financial_status = Column(String(50), default="En proceso de facturación")
    
    # Campos calculados por el backend (PostgreSQL Trigger)
    billed_minutes = Column(Integer, nullable=True)
    total_cost = Column(Float, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
