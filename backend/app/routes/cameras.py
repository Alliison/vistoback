from fastapi import APIRouter, HTTPException, Depends
import requests
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import AsyncSessionLocal as SessionLocal
from app.models import Camera, User, Patio
from app.utils.security import get_current_user

router = APIRouter(prefix="/cameras", tags=["Câmeras"])

MICRO_RTMP_URL = "http://vistotrack.com:9000/"
MICRO_AI_URL = "http://vistotrack.com:10000/"
MICRO_AI_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInVzZXJuYW1lIjoiYWxpc29uIiwiZXhwIjoxNzQyNDk1MTUwfQ.SkKiqe8-5-5Gagp2ngn2jTEwjSW8DG7_qsfrG9pKuBI"

# DB Session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Adiciona nova câmera com tipo e gera URL automaticamente
@router.post("/")
def adicionar_camera(camera_type: str, usuario: User = Depends(get_current_user), db: Session = Depends(get_db)):
    patio = db.query(Patio).filter(Patio.usuario_id == usuario.id).first()
    if not patio:
        raise HTTPException(status_code=404, detail="Pátio não encontrado para o usuário")

    payload = {"patio_id": patio.id, "camera_type": camera_type}
    response = requests.post(f"{MICRO_RTMP_URL}/start", json=payload)

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Erro ao gerar URL da câmera")

    data = response.json()
    nova_camera = Camera(tipo=camera_type, rtmp_url=data["rtmp_url"], patio_id=patio.id)
    db.add(nova_camera)
    db.commit()
    db.refresh(nova_camera)
    return {"status": "success", "camera_url": nova_camera.rtmp_url}

# Lista as transmissões ativas vinculadas ao sistema
@router.get("/ativas")
def listar_cameras_ativas(db: Session = Depends(get_db)):
    response = requests.get(f"{MICRO_RTMP_URL}/streams")
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Erro ao consultar o Micro RTMP")
    return response.json()

# Retorna o status de uma transmissão específica
@router.get("/{camera_id}/status")
def status_transmissao(camera_id: str):
    response = requests.get(f"{MICRO_RTMP_URL}/rtmp/status", params={"camera_id": camera_id})
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Erro ao obter status da transmissão")
    return response.json()

# Gera o link da transmissão
@router.get("/transmissao")
def visualizar_stream(camera_id: str):
    response = requests.get(f"{MICRO_RTMP_URL}/generate_stream_link", params={"camera_id": camera_id})
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Erro ao obter o link da transmissão")
    return response.json()

# Lista câmeras ativas do usuário autenticado
@router.get("/me")
def listar_minhas_cameras(usuario: User = Depends(get_current_user), db: Session = Depends(get_db)):
    patios = db.query(Patio).filter(Patio.usuario_id == usuario.id).all()
    patio_ids = [p.id for p in patios]

    response = requests.get(f"{MICRO_RTMP_URL}/streams")
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Erro ao obter transmissões")

    streams = [s for s in response.json().get("streams", []) if s.get("patio_id") in patio_ids]
    return {"status": "success", "streams": streams}
