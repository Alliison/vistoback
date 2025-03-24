from fastapi import APIRouter, HTTPException, Depends
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
MICRO_AI_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInVzZXJuYW1lIjoiYWxpc29uIiwiZXhwIjoxNzQyNDk1MTUwfQ.SkKiqe8-5-5Gagp2ngn2jTEwjSW8DG7_qsfrG9pKuBI" # Token de autenticação do Micro AI

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

# Endpoint para verificar o status de uma inspeção
@router.get("/inspecoes/status/{inspecao_id}", response_model=InspecaoResponse)
def get_inspecao_status(inspecao_id: int, db: Session = Depends(get_db)):
    """Retorna o status atual da inspeção."""
    inspecao = db.query(Inspecao).filter(Inspecao.id == inspecao_id).first()
    if not inspecao:
        raise HTTPException(status_code=404, detail="Inspeção não encontrada")
    
    return inspecao

# Endpoint para cancelar uma inspeção
@router.post("/inspecoes/cancelar")
def cancelar_inspecao(inspecao_id: int, db: Session = Depends(get_db)):
    """Permite que um condutor cancele uma inspeção pendente."""
    inspecao = db.query(Inspecao).filter(Inspecao.id == inspecao_id, Inspecao.status == "Pendente").first()
    if not inspecao:
        raise HTTPException(status_code=404, detail="Inspeção não encontrada ou já em andamento.")
    
    inspecao.status = "Cancelada"
    db.commit()
    return {"status": "success", "message": "Inspeção cancelada com sucesso."}

# Endpoint para finalizar uma inspeção
@router.post("/inspecoes/finalizar")
def finalizar_inspecao(inspecao_id: int, resultado: str, db: Session = Depends(get_db)):
    """Permite que um inspetor finalize uma inspeção e registre o resultado."""
    inspecao = db.query(Inspecao).filter(Inspecao.id == inspecao_id, Inspecao.status == "Iniciada").first()
    if not inspecao:
        raise HTTPException(status_code=404, detail="Inspeção não encontrada ou já finalizada.")
    
    inspecao.status = "Concluída"
    inspecao.resultado = resultado
    db.commit()
    return {"status": "success", "message": "Inspeção finalizada com sucesso."}

# Endpoint para listar histórico de inspeções
@router.get("/inspecoes/historico")
def listar_historico(user_email: str, db: Session = Depends(get_db)):
    """Retorna o histórico de inspeções para um usuário específico."""
    historico = db.query(Inspecao).filter(Inspecao.usuario_email == user_email).all()
    return historico

# Endpoint para um condutor agendar uma inspeção
@router.post("/inspecoes/agendar", response_model=AgendamentoResponse)
def agendar_inspecao(agendamento_data: AgendamentoResponse, db: Session = Depends(get_db)):
    """Condutores agendam inspeções para serem analisadas posteriormente."""
    novo_agendamento = Agendamento(
        usuario_id=agendamento_data.usuario_id,
        data=agendamento_data.data,
        horario=agendamento_data.horario,
        local=agendamento_data.local,
        status="Pendente"
    )
    db.add(novo_agendamento)
    db.commit()
    db.refresh(novo_agendamento)
    return novo_agendamento

# Endpoint para listar inspeções pendentes (para inspetores visualizarem a agenda)
@router.get("/inspecoes/listar", response_model=List[AgendamentoResponse])  # ✅ Corrigido para Python 3.8
def listar_inspecoes(db: Session = Depends(get_db)):
    """Lista todas as inspeções pendentes para que os inspetores possam visualizar a agenda."""
    agendamentos = db.query(Agendamento).filter(Agendamento.status == "Pendente").all()
    return agendamentos

# Endpoint para inspetores iniciarem uma inspeção
@router.post("/inspecoes/start", response_model=InspecaoResponse)
def iniciar_inspecao(inspecao_data: InspecaoCreate, db: Session = Depends(get_db)):
    """Permite que inspetores iniciem uma inspeção validando a presença de câmeras ativas."""
    cameras = db.query(Camera).filter(Camera.patio_id == inspecao_data.patio_id).all()
    if not cameras or len(cameras) < 4:
        raise HTTPException(status_code=400, detail="O pátio precisa ter pelo menos 4 câmeras cadastradas.")
    
    cameras_ativas = []
    for camera in cameras:
        rtmp_response = requests.get(MICRO_RTMP_URL, params={"camera_id": camera.id})
        if rtmp_response.status_code == 200 and rtmp_response.json().get("status") == "active":
            cameras_ativas.append(camera.id)
    
    if len(cameras_ativas) < 4:
        raise HTTPException(status_code=400, detail="Pelo menos 4 câmeras precisam estar ativas para iniciar a inspeção.")
    
    ai_payload = {"patio_id": inspecao_data.patio_id}
    ai_headers = {"Authorization": f"Bearer {MICRO_AI_TOKEN}"}
    ai_response = requests.post(MICRO_AI_URL, json=ai_payload, headers=ai_headers)
    if ai_response.status_code != 200:
        raise HTTPException(status_code=500, detail="Erro ao iniciar o Micro AI.")
    
    nova_inspecao = Inspecao(
        usuario_email=inspecao_data.usuario_email,
        data=datetime.utcnow().date(),
        placa=inspecao_data.placa,
        status="Em andamento"
    )
    db.add(nova_inspecao)
    db.commit()
    db.refresh(nova_inspecao)
    return nova_inspecao

# Endpoint para inspetores finalizarem uma inspeção
@router.post("/inspecoes/finalizar")
def finalizar_inspecao(inspecao_id: int, resultado: str, db: Session = Depends(get_db)):
    """Permite que um inspetor finalize uma inspeção e registre o resultado."""
    inspecao = db.query(Inspecao).filter(Inspecao.id == inspecao_id, Inspecao.status == "Em andamento").first()
    if not inspecao:
        raise HTTPException(status_code=404, detail="Inspeção não encontrada ou já finalizada.")
    
    inspecao.status = "Concluída"
    inspecao.resultado = resultado
    db.commit()
    return {"status": "success", "message": "Inspeção finalizada com sucesso."}
