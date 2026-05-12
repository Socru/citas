from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Text, Boolean, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Empresa(Base):
    """ negocio suscrito al SaaS"""
    __tablename__ = 'empresas'
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False) 
    subdominio = Column(String(100), unique=True, index=True, nullable=False)
    telefono = Column(String(20))
    configuracion = Column(JSON, default={}) 
    
    usuarios = relationship("Usuario", back_populates="empresa", cascade="all, delete")
    clientes = relationship("Cliente", back_populates="empresa", cascade="all, delete")
    citas = relationship("Cita", back_populates="empresa", cascade="all, delete")

class Usuario(Base):
    """ personal (Admin, Profesional, Asistente)"""
    __tablename__ = 'usuarios'
    
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey('empresas.id'), nullable=False)
    nombre = Column(String(255), nullable=False)
    correo = Column(String(255), unique=True, index=True, nullable=False)
    contrasena_hash = Column(String(255), nullable=False)
    rol = Column(String(50), default="asistente")
    
    # Fundamental para no perder el historial de un empleado que ya no trabaja ahí
    activo = Column(Boolean, default=True) 
    
    empresa = relationship("Empresa", back_populates="usuarios")

class Cliente(Base):
    """Los pacientes o clientes del negocio"""
    __tablename__ = 'clientes'
    
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey('empresas.id'), nullable=False)
    nombre = Column(String(255), nullable=False)
    telefono = Column(String(20), nullable=False)
    correo = Column(String(255)) 
    
    empresa = relationship("Empresa", back_populates="clientes")
    citas = relationship("Cita", back_populates="cliente", cascade="all, delete")

class Cita(Base):
    """La agenda y reservas"""
    __tablename__ = 'citas'
    
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey('empresas.id'), nullable=False)
    cliente_id = Column(Integer, ForeignKey('clientes.id'), nullable=False)
    
    fecha_hora = Column(DateTime, nullable=False)
    motivo = Column(Text) 
    duracion_minutos = Column(Integer, default=30) 
    estado = Column(String(50), default="activa") 
    
    # notas importantes
    notas_internas = Column(Text) 
    
    empresa = relationship("Empresa", back_populates="citas")
    cliente = relationship("Cliente", back_populates="citas")

class Cuenta(Base):
    __tablename__ = "cuentas"
    id= Column (Integer, primary_key = True, index=True)
    empresa_id = Column (Integer, ForeignKey("empresas.id"))
    client_id = Column (Integer, ForeignKey("clientes.id"))
    concepto = Column(String(255)) #especificacion
    monto_total= Column(Float) #total del costo
    saldo_pendiente=Column(Float) #resto
    estado = Column(String(50), default="pendiente") #pendiente/pagado
    fecha_creacion = Column(DateTime,default=datetime.utcnow)


class Pago(Base):
    __tablename__ = "pagos"
    id = Column(Integer, primary_key=True, index=True)
    cuenta_id = Column(Integer,ForeignKey("cuentas.id"))#vinculo a cuenta deuda
    monto = Column(Float) #abonar
    metodo_pago = Column(String(50)) #Efectivo/transferencia/tc
    fecha_pago = Column(DateTime, default =datetime.utcnow)
