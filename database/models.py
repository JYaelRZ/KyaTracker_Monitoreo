from sqlalchemy import Column, String, Float, Integer, DateTime, Boolean
from datetime import datetime, timezone
import uuid
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

class ClientStatus(Base):
    """Modelo para estado de clientes (Activo/Inactivo)"""
    __tablename__ = "client_statuses"
    
    client = Column(String(150), primary_key=True)
    is_active = Column(Boolean, default=True)

class User(Base):
    """Modelo para usuarios del sistema"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(150), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(50), default="normal") # 'admin' o 'normal'
    permissions = Column(String(255), default="[]") # JSON list of permissions
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

