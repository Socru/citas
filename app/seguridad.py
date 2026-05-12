from passlib.context import CryptContext
#bcrypt para encriptar
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import database, models
from fastapi.security import OAuth2PasswordBearer


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#token key
SECRET_KEY="CLAVE"
ALGORITHM="HS256"
ACCES_TOKEN_EXPIRE_MINUTES = 59

#autorizar, fast api la ruta de token mediante login

oauth2_scheme=OAuth2PasswordBearer(tokenUrl="login")


def encriptar_contrasena(contrasena: str) -> str:
    #texto a hash
    return pwd_context.hash(contrasena)

def verificar_contrasena(contrasena_texto:str, contrasena_encriptada:str)-> bool:
    #verificacion de la contrasena
    return pwd_context.verify(contrasena_texto,contrasena_encriptada)
    
def crear_token_acceso(data:dict):
    #crear token para usuarios y autocierre
    a_encriptar =data.copy()
    expirar= datetime.now(timezone.utc)+ timedelta(minutes=ACCES_TOKEN_EXPIRE_MINUTES)
    a_encriptar.update({"exp":expirar})

    #token llave secreta
    token_jwt=jwt.encode(a_encriptar, SECRET_KEY, algorithm=ALGORITHM)
    return token_jwt

#privilegios
def obtener_usuario_actual(token:str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credenciales_excepcion = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate":"Bearer"},
    )
    try:
        #desencriptar token
        payload = jwt.decode(token, SECRET_KEY, algorithms= [ALGORITHM])
        correo: str = payload.get("sub")
        if correo is None:
            raise credenciales_excepcion
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="El token ha expirado")
    except jwt.InvalidTokenError:
        raise credenciales_excepcion

        #buscar usuario si existe
    usuario = db.query(models.Usuario).filter(models.Usuario.correo==correo).first()
    if usuario is None:
        raise credenciales_excepcion

        #si esta bien
    return usuario

