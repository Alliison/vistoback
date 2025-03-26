from pydantic import BaseModel, EmailStr
from datetime import date, time
from typing import Optional  # 🔹 Importação corrigida para Python 3.8

# 🔹 Base de Usuário: Campos comuns para reaproveitamento
class UserBase(BaseModel):
    nome: str
    email: EmailStr

# 🔹 Esquema para criação de usuário (entrada da requisição)
class UserCreate(UserBase):
    telefone: str
    senha: str

# 🔹 Esquema de resposta ao criar usuário (evita retornar a senha)
class UserResponse(UserBase):
    id: int
    role: str
    class Config:
        orm_mode = True  # Permite conversão do SQLAlchemy para Pydantic

# Esquema para login do usuário
class UserLogin(BaseModel):
    email: EmailStr
    senha: str

# Esquema para resposta do token
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    sub: str
    name: str
    role: str 


# 🔹 Schema para criação de um agendamento
class AgendamentoCreate(BaseModel):
    data: date
    horario: time
    local: str

# 🔹 Schema para exibir um agendamento
class AgendamentoResponse(AgendamentoCreate):
    id: int
    usuario_id: int
    status: str
    class Config:
        orm_mode = True  # Permite conversão automática do SQLAlchemy para Pydantic

# 🔹 Schema para criação de uma inspeção
class InspecaoCreate(BaseModel):
    usuario_email: EmailStr
    data: date
    placa: str
    patio_id: int  # 🔹 Relacionamento com o pátio

# 🔹 Schema para exibição de uma inspeção
class InspecaoResponse(InspecaoCreate):
    id: int
    status: str
    resultado: Optional[str] # Adicionando campo para resultado da inspeção
    class Config:
        orm_mode = True

class FinalizarInspecao(BaseModel):
    concluido_por: EmailStr
    notas: str

# 🔹 Schema para criação de um pátio
class PatioCreate(BaseModel):
    nome: str

# 🔹 Schema para exibição de um pátio
class PatioResponse(PatioCreate):
    id: int
    usuario_id: int
    class Config:
        orm_mode = True

# 🔹 Schema para criação de uma câmera
class CameraCreate(BaseModel):
    camera_type: str

# 🔹 Schema para exibição de uma câmera
class CameraResponse(BaseModel):
    id: int
    tipo: str
    rtmp_url: str

    class Config:
        orm_mode = True

class VeiculoCreate(BaseModel):
    placa: str
    modelo: str
    ano: int
    cor: str
    km: int

class VeiculoResponse(BaseModel):
    id: int
    placa: str
    modelo: str
    ano: int
    cor: str
    km: int

    class Config:
        orm_mode = True

# 🔹 Schema para criação de relatório
class RelatorioCreate(BaseModel):
    veiculo_id: int
    inspecao_id: int
    data: Optional[date] = None
    resultado: str
    arquivo_pdf: Optional[str] = None

# 🔹 Schema para resposta de relatório
class RelatorioResponse(RelatorioCreate):
    id: int

    class Config:
        orm_mode = True