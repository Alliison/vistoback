from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import Veiculo
from app.schemas import VeiculoCreate, VeiculoResponse #, VeiculoUpdate
from app.utils.security import get_current_user
from app.models import User as Usuario
from typing import List

router = APIRouter(prefix="/veiculos", tags=["Veículos"])

@router.get("/", response_model=List[VeiculoResponse])
async def listar_veiculos(db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    result = await db.execute(select(Veiculo).where(Veiculo.usuario_id == usuario.id))
    return result.scalars().all()

@router.post("/", response_model=VeiculoResponse)
async def criar_veiculo(dados: VeiculoCreate, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    novo_veiculo = Veiculo(**dados.dict(), usuario_id=usuario.id)
    db.add(novo_veiculo)
    await db.commit()
    await db.refresh(novo_veiculo)
    return novo_veiculo

@router.get("/{veiculo_id}", response_model=VeiculoResponse)
async def obter_veiculo(veiculo_id: int, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    result = await db.execute(select(Veiculo).where(Veiculo.id == veiculo_id, Veiculo.usuario_id == usuario.id))
    veiculo = result.scalar_one_or_none()
    if not veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    return veiculo

# @router.put("/{veiculo_id}", response_model=VeiculoResponse)
# async def atualizar_veiculo(veiculo_id: int, dados: VeiculoUpdate, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
#     result = await db.execute(select(Veiculo).where(Veiculo.id == veiculo_id, Veiculo.usuario_id == usuario.id))
#     veiculo = result.scalar_one_or_none()
#     if not veiculo:
#         raise HTTPException(status_code=404, detail="Veículo não encontrado ou não autorizado")

#     for campo, valor in dados.dict(exclude_unset=True).items():
#         setattr(veiculo, campo, valor)

#     await db.commit()
#     await db.refresh(veiculo)
#     return veiculo

@router.delete("/{veiculo_id}")
async def deletar_veiculo(veiculo_id: int, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    result = await db.execute(select(Veiculo).where(Veiculo.id == veiculo_id, Veiculo.usuario_id == usuario.id))
    veiculo = result.scalar_one_or_none()
    if not veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado ou não autorizado")

    await db.delete(veiculo)
    await db.commit()
    return {"detail": "Veículo removido com sucesso"}
