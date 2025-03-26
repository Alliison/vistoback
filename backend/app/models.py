from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey, Text
from .database import Base
from sqlalchemy.orm import relationship

# 🔹 Base de Usuário: Campos comuns para reaproveitamento
class Veiculo(Base):
    __tablename__ = "veiculos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("users.id"))
    placa = Column(String, unique=True, index=True, nullable=False)
    modelo = Column(String, nullable=False)
    ano = Column(Integer, nullable=False)
    cor = Column(String, nullable=True)
    km = Column(Integer, nullable=True)

    usuario = relationship("User", back_populates="veiculos")
    relatorios = relationship("Relatorio", back_populates="veiculo", cascade="all, delete-orphan")


class Relatorio(Base):
    __tablename__ = "relatorios"

    id = Column(Integer, primary_key=True, index=True)
    veiculo_id = Column(Integer, ForeignKey("veiculos.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    inspecao_id = Column(Integer, ForeignKey("inspecoes.id"), nullable=False)
    data = Column(Date, nullable=False)
    resultado = Column(String, nullable=False)
    arquivo_pdf = Column(String, nullable=True)

    veiculo = relationship("Veiculo", back_populates="relatorios")
    usuario = relationship("User")
    inspecao = relationship("Inspecao")



class User(Base):
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}  # 🔹 Adicionando essa opção

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    telefone = Column(String(20), nullable=False)
    senha = Column(String(255), nullable=False)
    role = Column(String(20), default="user")

    agendamentos = relationship("Agendamento", back_populates="usuario", cascade="all, delete-orphan")
    patios = relationship("Patio", back_populates="usuario", cascade="all, delete-orphan")
    veiculos = relationship("Veiculo", back_populates="usuario", cascade="all, delete-orphan")


class Agendamento(Base):
    __tablename__ = "agendamentos"
    __table_args__ = {"extend_existing": True}  # 🔹 Garante que a tabela não será redefinida

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    data = Column(Date, nullable=False)
    horario = Column(Time, nullable=False)
    local = Column(String(100), nullable=False)
    status = Column(String(20), default="Pendente")

    usuario = relationship("User", back_populates="agendamentos")


class Inspecao(Base):
    __tablename__ = "inspecoes"
    __table_args__ = {"extend_existing": True}  # 🔹 Garante que a tabela não será redefinida

    id = Column(Integer, primary_key=True, index=True)
    usuario_email = Column(String, ForeignKey("users.email"), nullable=False)
    data = Column(Date, nullable=False)
    placa = Column(String(10), nullable=False)
    status = Column(String(20), default="Pendente")
    resultado = Column(Text, nullable=True)  # Adicionando campo para resultado da inspeção
    patio_id = Column(Integer, ForeignKey("patios.id"), nullable=False)  # Relacionando com pátio

    patio = relationship("Patio")


class Patio(Base):
    __tablename__ = "patios"
    __table_args__ = {"extend_existing": True}  # 🔹 Garante que a tabela não será redefinida

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    usuario_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    usuario = relationship("User", back_populates="patios")
    cameras = relationship("Camera", back_populates="patio", cascade="all, delete-orphan")


class Camera(Base):
    __tablename__ = "cameras"
    __table_args__ = {"extend_existing": True}  # 🔹 Garante que a tabela não será redefinida

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(50), nullable=False)
    rtmp_url = Column(String(255), nullable=False)
    patio_id = Column(Integer, ForeignKey("patios.id"), nullable=False)

    patio = relationship("Patio", back_populates="cameras")
