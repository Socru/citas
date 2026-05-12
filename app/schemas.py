from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

# para las empresas
class EmpresaBase(BaseModel):
        nombre:str
        subdominio:str
        telefono: Optional [str] = None
        configuracion: Optional[Dict[str, Any]] = {}

class EmpresaCreate(EmpresaBase):
    pass

class EmpresaResponse(EmpresaBase):
    id: int

    class Config:
        from_attributes= True

# Usuarios
class UsuarioBase (BaseModel):
    nombre: str
    correo: str
    rol : str = "asistente"
    activo:  bool = True

class UsuarioCreate(UsuarioBase):
    contrasena: str

class UsuarioResponse(UsuarioBase):
    id:int
    empresa_id: int

    class Config:
        from_attributes = True

#Clientes

class ClienteBase(BaseModel):
    nombre: str
    telefono: str
    correo: Optional[str] = None

class ClienteCreate(ClienteBase):
    pass

class ClienteResponse(ClienteBase):
    id: int
    empresa_id: int

    class Config:
        from_attributes= True

#Citas
class CitaBase(BaseModel):
    cliente_id: int
    fecha_hora: datetime
    motivo: Optional[str] = None
    duracion_minutos: int=30
    estado: str ="activa"
    notas_internas: Optional[str] = None

class CitaCreate(CitaBase):
    pass

class CitaResponse(CitaBase):
    id: int
    empresa_id: int

    class Config:
        from_attributes= True

class CitaUpdate(BaseModel):
    fecha_hora: Optional[datetime]= None
    motivo: Optional [str]= None
    duracion_minutos: Optional[int]= None
    estado: Optional [str] = None
    notas_internas: Optional [str] =None

#Cuentas/deudas

class CuentaBase(BaseModel):
    cliente_id: int
    concepto: str
    monto_total: float

class CuentaCreate(CuentaBase):
    pass

class CuentaResponse(CuentaBase):
    id: int
    empresa_id: int
    saldo_pendiente: float
    estado: str
    fecha_creacion: datetime
    class Config:
        from_attributes= True

#Pagos o abonos

class PagoBase(BaseModel):
    cuenta_id: int
    monto: float
    metodo_pago: str #tarjeta/efectivo

class PagoCreate(PagoBase):
    pass

class PagoResponse(PagoBase):
    id: int
    fecha_pago: datetime

    class Config:
        from_attributes = True