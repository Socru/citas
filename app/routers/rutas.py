from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, database, seguridad
from typing import List
from fastapi.security import OAuth2PasswordRequestForm
from .. seguridad import verificar_contrasena, crear_token_acceso

#router para agrupar url
router = APIRouter()

@router.post("/empresas/", response_model=schemas.EmpresaResponse)
def crear_empresa(empresa: schemas.EmpresaCreate, db: Session = Depends(database.get_db)):
#crea nueva empresa
#verificacion de no duplicidad
    empresa_existente= db.query(models.Empresa).filter(models.Empresa.subdominio == empresa.subdominio).first()
    if empresa_existente:
        raise  HTTPException(status_code=400,detail="Dominio en existencia")

    #datos para sql model dump y pydantic
    nueva_empresa = models.Empresa(**empresa.model_dump())

    #guardamos en la base
    db.add(nueva_empresa)
    db.commit()
    db.refresh(nueva_empresa)

    return nueva_empresa

#mostrar todas las empresas
@router.get("/empresas", response_model=List[schemas.EmpresaResponse])
def obtener_empresas(db: Session = Depends (database.get_db)):
    #listar registradas
    empresas = db.query(models.Empresa).all()
    return empresas

#crear usuario para empresa
@router.post("/empresas/{empresa_id}/usuarios/", response_model=schemas.UsuarioResponse)
def crear_usuario_empresa(empresa_id: int, usuario: schemas.UsuarioCreate, db: Session = Depends (database.get_db)):
#registra empleado o administrador de empresa

#validamos la empresa a la que queremos ingresar el usuario exista
    empresa = db.query(models.Empresa).filter(models.Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="empresa inexistente")

    #validamos correo no repetido
    correo_existente = db.query(models.Usuario).filter(models.Usuario.correo == usuario.correo).first()
    if correo_existente:
        raise HTTPException(status_code=400, detail="correo ya registrado")

    #Crear usuario y vincularlo
    #aun no encriptado
    nuevo_usuario = models.Usuario(
        empresa_id= empresa_id,
        nombre= usuario.nombre,
        correo= usuario.correo,
        contrasena_hash = seguridad.encriptar_contrasena(usuario.contrasena),
        rol= usuario.rol,
        activo= usuario.activo

    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return nuevo_usuario

#get clientes empresa

@router.get("/empresas/{empresa_id}/clientes", response_model=List[schemas.ClienteResponse])

def obtener_clientes_empresa(empresa_id: int, db: Session= Depends(database.get_db), usuario_actual: models.Usuario = Depends(seguridad.obtener_usuario_actual)):
    #LISTA DE CLIENTES DE EMPRESA 

    #validar existencia
    empresa = db.query(models.Empresa).filter(models.Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail = "Empresa inexistente")
    #verificar limitacion por empresa
    if usuario_actual.empresa_id != empresa_id:
        raise HTTPException(status_code=403,detail="permisos denegados")
    clientes= db.query(models.Cliente).filter(models.Cliente.empresa_id== empresa.id).all()
    return clientes


#crear un cliente para empresa post

@router.post("/empresas/{empresa_id}/clientes/", response_model=schemas.ClienteResponse)
def crear_cliente_empresa(empresa_id:int,cliente: schemas.ClienteCreate, db: Session = Depends(database.get_db), usuario_actual:models.Usuario=Depends(seguridad.obtener_usuario_actual)):
    #"registrar cliente, paciente, etc"
    #validamos existencia
    empresa = db.query(models.Empresa).filter(models.Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="empresa inexistente")

    if usuario_actual.empresa_id !=empresa_id:
        raise HTTPException(status_code=404, detail="permiso denegado")

    #nuevo cliente con id de empresa
    nuevo_cliente = models.Cliente(
        empresa_id  = empresa_id,
        nombre = cliente.nombre,
        telefono = cliente.telefono,
        correo = cliente.correo
    )

    # guardar en la base
    db.add(nuevo_cliente)
    db.commit()
    db.refresh(nuevo_cliente)

    return nuevo_cliente

# citas 
@router.post("/empresas/{empresa_id}/citas/", response_model=schemas.CitaResponse)
def agendar_cita(empresa_id: int, cita: schemas.CitaCreate, db: Session= Depends(database.get_db), usuario_actual: models.Usuario = Depends(seguridad.obtener_usuario_actual)):
    # validar que la empresa exista
    empresa = db.query (models.Empresa).filter(models.Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Cliente inexiste")

    if usuario_actual.empresa_id != empresa_id:
        raise HTTPException(status_code=403, detail="permiso denegado")

    # crear la cita
    nueva_cita = models.Cita(
        empresa_id = empresa_id,
        cliente_id = cita.cliente_id,
        fecha_hora = cita.fecha_hora,
        motivo= cita.motivo,
        duracion_minutos = cita.duracion_minutos,
        estado = cita.estado,
        notas_internas = cita.notas_internas
    )

    db.add(nueva_cita)
    db.commit()
    db.refresh(nueva_cita)
    return nueva_cita

#obtener citas de empresa 
@router.get("/empresas/{empresa_id}/citas/", response_model=List[schemas.CitaResponse])

def obtener_citas_empresa(empresa_id:int, db: Session = Depends(database.get_db), usuario_actual: models.Usuario =Depends(seguridad.obtener_usuario_actual)):
    #agenda completa de empresa

    if usuario_actual.empresa_id!= empresa_id:
        raise HTTPException(status_code=403, detail="permiso denegado")

    citas= db.query(models.Cita).filter(models.Cita.empresa_id == empresa_id).all()
    return citas

#actualizar cancelar una citas mediante put
@router.put("/empresas/{empresa_id}/citas/{cita_id}", response_model=schemas.CitaResponse)

def actualizar_cita(empresa_id: int, cita_id: int, cita_actualizada: schemas.CitaUpdate, db:Session= Depends(database.get_db), usuario_actual: models.Usuario = Depends(seguridad.obtener_usuario_actual)):

    if usuario_actual.empresa_id != empresa_id:
        raise HTTPException(status_code=403, detail="permiso denegado")
    #Cambiar la fecha o datos


    #buscamos la cita
    cita_db= db.query(models.Cita).filter(models.Cita.id == cita_id, models.Cita.empresa_id == empresa_id).first()
    if not cita_db:
        raise HTTPException(status_code=404, detail="cita inexistente")
    #actualizamos lo requerido

    datos_nuevos = cita_actualizada.model_dump(exclude_unset=True)
    for clave, valor in datos_nuevos.items():
        setattr(cita_db, clave, valor)

    db.commit()
    db.refresh(cita_db)
    return citas
        
#login
@router.post("/login")
def iniciar_sesion(from_data: OAuth2PasswordRequestForm= Depends(), db: Session = Depends(database.get_db)):
    #verificar credenciales y regresar token

    #buscar usuario por correo username
    usuario= db.query(models.Usuario).filter(models.Usuario.correo== from_data.username).first()
    #problema en usuario o contrasena

    if not usuario or not verificar_contrasena(from_data.password, usuario.contrasena_hash):
        raise HTTPException(status_code=400, detail="usuario o password incorrecto")

    #si existe, ingresamos y guardamos el correo segun la empresa
    token = crear_token_acceso(data={"sub": usuario.correo, "empresa_id":usuario.empresa_id})
    return {"access_token": token, "token_type": "bearer"}

    # crear cuenta deuda total

@router.post("/empresas/{empresa_id}/cuentas/", response_model=schemas.CuentaResponse)
def crear_cuenta(
    empresa_id: int,
    cuenta: schemas.CuentaCreate,
    db: Session = Depends(database.get_db),
    usuario_actual: models.Usuario = Depends(seguridad.obtener_usuario_actual)
):
    #seguridad verificar permisos
    if usuario_actual.empresa_id!= empresa_id:
        raise HTTPException(status_code=403, detail="permiso denegado")

    #verificar cliente existente de la empresa
    cliente = db.query(models.Cliente).filter(
        models.Cliente.id == cuenta.cliente_id,
        models.Cliente.empresa_id == empresa_id
    ).first()

    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    #crear deuda inicial a monto total
    nueva_cuenta= models.Cuenta(
        empresa_id= empresa_id,
        cliente_id= cuenta.cliente_id,
        concepto = cuenta.concepto,
        monto_total= cuenta.monto_total,
        saldo_pendiente= cuenta.monto_total,
        estado = "pendiente"
    )
    db.add(nueva_cuenta)
    db.commit()
    db.refresh(nueva_cuenta)
    return nueva_cuenta

#registrar pago o abono
@router.post("/empresas/{empresa_id}/pagos/", response_model=schemas.PagoResponse)
def registrar_pago(
    empresa_id: int,
    pago: schemas.PagoCreate,
    db: Session = Depends(database.get_db),
    usuario_actual: models.Usuario = Depends(seguridad.obtener_usuario_actual)
):

    if usuario_actual.empresa_id != empresa_id:
        raise HTTPException(status_code=403, detail ="permiso denegado")
        #buscar cuenta a la que se abona
    cuenta = db.query(models.Cuenta).filter(
        models.Cuenta.id == pago.cuenta_id,
        models.Cuenta.empresa_id == empresa_id
    ).first()

    if not cuenta:
        raise HTTPException(status_code=404, detail="cuenta no encontrada")

    #verificar no pagar mas
    if cuenta.saldo_pendiente < pago.monto:
        raise HTTPException(status_code=400, detail="El abono ({pago.monto}) supera la deuda ({cuenta.saldo_pendiente})")
    #registrar el pago en el historial

    nuevo_pago =models.Pago(
        cuenta_id= pago.cuenta_id,
        monto= pago.monto,
        metodo_pago=pago.metodo_pago
    )

    db.add(nuevo_pago)

    #restar automaticamente de la cuenta
    cuenta.saldo_pendiente-=pago.monto
    #si esta liquidado, cambiar estado
    if cuenta.saldo_pendiente <= 0:
        cuenta.estado ="pagado"

    db.commit()
    db.refresh(nuevo_pago)
    return nuevo_pago
