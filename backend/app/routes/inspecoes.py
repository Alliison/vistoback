from fastapi import APIRouter, HTTPException, Depends, status
import requests
from typing import List
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import AsyncSessionLocal as SessionLocal
from app.models import Inspecao, Camera, User, Agendamento
from app.schemas import InspecaoResponse, AgendamentoResponse, InspecaoCreate
from app.utils.security import get_current_user

router = APIRouter()

# Configurações
MICRO_RTMP_URL = "http://vistotrack.com:9000/"
MICRO_AI_URL = "http://vistotrack.com:10000"
MICRO_AI_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInVzZXJuYW1lIjoiYWxpc29uIiwiZXhwIjoxNzQyNDk1MTUwfQ.SkKiqe8-5-5Gagp2ngn2jTEwjSW8DG7_qsfrG9pKuBI"

# Dependência para acessar o banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Função para salvar logs no banco de dados
def save_log(event: str, message: str, db: Session):
    log_entry = Inspecao(evento=event, mensagem=message, timestamp=datetime.utcnow())
    db.add(log_entry)
    db.commit()

@router.get("/inspecoes/{id}", response_model=InspecaoResponse)
def obter_inspecao(id: int, db: Session = Depends(get_db)):
    """Consulta detalhes completos de uma inspeção específica."""
    inspecao = db.query(Inspecao).filter(Inspecao.id == id).first()
    if not inspecao:
        raise HTTPException(status_code=404, detail="Inspeção não encontrada")
    return inspecao

@router.put("/inspecoes/{id}/finalizar")
def finalizar_inspecao_atualizada(id: int, body: dict, db: Session = Depends(get_db)):
    """Finaliza uma inspeção em andamento, adicionando observações."""
    inspecao = db.query(Inspecao).filter(Inspecao.id == id, Inspecao.status == "Em andamento").first()
    if not inspecao:
        raise HTTPException(status_code=404, detail="Inspeção não encontrada ou já finalizada.")

    inspecao.status = "Concluída"
    inspecao.resultado = body.get("notas")
    db.commit()
    return {"status": "success", "message": "Inspeção finalizada com sucesso."}
