from fastapi import APIRouter, HTTPException, Request, Depends
import json
import requests
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import AsyncSessionLocal as SessionLocal
from app.models import Camera, User, Patio

router = APIRouter()

# Configurações
MICRO_RTMP_URL = "http://vistotrack.com:9000/"
MICRO_AI_URL = "http://vistotrack.com:10000/"
MICRO_AI_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInVzZXJuYW1lIjoiYWxpc29uIiwiZXhwIjoxNzQyNDk1MTUwfQ.SkKiqe8-5-5Gagp2ngn2jTEwjSW8DG7_qsfrG9pKuBI"  # Token de autenticação do Micro AI

# Dependência para acessar o banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Função para salvar logs no banco de dados
def save_log(event: str, message: str, db: Session):
    log_entry = Camera(evento=event, mensagem=message, timestamp=datetime.utcnow())
    db.add(log_entry)
    db.commit()

# Adicionar uma nova câmera
@router.post("/cameras/add")
def add_camera(user_id: int, camera_type: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    patios = db.query(Patio).filter(Patio.user_id == user_id).all()
    if not patios:
        raise HTTPException(status_code=404, detail="Nenhum pátio encontrado para este usuário")
    
    patio_id = patios[0].id  # Assumindo que um usuário só gerencia um pátio para simplificação
    payload = {"patio_id": patio_id, "camera_type": camera_type}
    response = requests.post(f"{MICRO_RTMP_URL}/start", json=payload)
    
    if response.status_code != 200:
        save_log("error", f"Erro ao adicionar câmera: {response.text}", db)
        return {"status": "error", "message": "Erro ao adicionar câmera."}
    
    data = response.json()
    return {"status": "success", "camera_url": data["rtmp_url"]}

# Remover uma câmera
@router.delete("/cameras/remove")
def remove_camera(camera_id: str, db: Session = Depends(get_db)):
    payload = {"camera_id": camera_id}
    response_rtmp = requests.post(f"{MICRO_RTMP_URL}/stop", json=payload)
    response_ai = requests.post(f"{MICRO_AI_URL}/stop_patio", json=payload)
    
    if response_rtmp.status_code != 200 or response_ai.status_code != 200:
        save_log("error", "Erro ao remover câmera", db)
        return {"status": "error", "message": "Erro ao remover câmera."}
    
    return {"status": "success", "message": "Câmera removida com sucesso."}

# Listar transmissões ativas para um usuário
@router.get("/cameras/listartransmissoes")
def listar_transmissoes(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    patios = db.query(Patio).filter(Patio.user_id == user_id).all()
    patio_ids = [p.id for p in patios]
    
    response = requests.get(f"{MICRO_RTMP_URL}/streams")
    if response.status_code != 200:
        return {"status": "error", "message": "Erro ao obter transmissões."}
    
    streams = [s for s in response.json()["streams"] if s["patio_id"] in patio_ids]
    return {"status": "success", "streams": streams}

# Status de uma câmera específica
@router.get("/cameras/statustransmissoes")
def status_transmissao(camera_id: str):
    response = requests.get(f"{MICRO_RTMP_URL}/rtmp/status", params={"camera_id": camera_id})
    if response.status_code != 200:
        return {"status": "error", "message": "Erro ao obter status da câmera."}
    
    return response.json()

# Exibir stream de uma câmera
@router.get("/cameras/transmissao")
def visualizar_stream(user_id: int, camera_id: str):
    response = requests.get(f"{MICRO_RTMP_URL}/generate_stream_link", params={"camera_id": camera_id})
    if response.status_code != 200:
        return {"status": "error", "message": "Erro ao obter link da câmera."}
    
    return response.json()
