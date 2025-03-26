from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import Agendamento, User
from app.schemas import AgendamentoCreate, AgendamentoResponse
from app.utils.security import get_current_user
from typing import List  # 🔹 Importando List corretamente

router = APIRouter(prefix="/agenda", tags=["Agenda"])

@router.get("/", response_model=List[AgendamentoResponse])
async def listar_agendamentos(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user_stmt = select(User.id).where(User.email == current_user["email"])
    user_result = await db.execute(user_stmt)
    user_id = user_result.scalar()

    if not user_id:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    stmt = select(Agendamento).where(Agendamento.usuario_id == user_id)
    result = await db.execute(stmt)
    agendamentos = result.scalars().all()

    return agendamentos



@router.post("/", response_model=AgendamentoResponse)
async def criar_agendamento(
    agendamento: AgendamentoCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    novo_agendamento = Agendamento(**agendamento.dict(), email_condutor=current_user["email"])
    db.add(novo_agendamento)
    await db.commit()
    await db.refresh(novo_agendamento)
    return novo_agendamento


@router.put("/{agendamento_id}")
async def reagendar_agendamento(
    agendamento_id: int,
    data_nova: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Agendamento).where(
        Agendamento.id == agendamento_id,
        Agendamento.email_condutor == current_user["email"]
    )
    result = await db.execute(stmt)
    agendamento = result.scalars().first()

    if not agendamento:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")

    agendamento.data = data_nova["data"]
    await db.commit()
    await db.refresh(agendamento)
    return {"message": "Agendamento atualizado com sucesso"}


@router.delete("/{agendamento_id}")
async def cancelar_agendamento(
    agendamento_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Agendamento).where(
        Agendamento.id == agendamento_id,
        Agendamento.email_condutor == current_user["email"]
    )
    result = await db.execute(stmt)
    agendamento = result.scalars().first()

    if not agendamento:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")

    await db.delete(agendamento)
    await db.commit()
    return {"message": "Agendamento cancelado com sucesso"}


@router.get("/resumo")
async def resumo_agendamentos(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user_stmt = select(User.id).where(User.email == current_user["email"])
    user_result = await db.execute(user_stmt)
    user_id = user_result.scalar()

    if not user_id:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    stmt = select(Agendamento).where(Agendamento.usuario_id == user_id)
    result = await db.execute(stmt)
    agendamentos = result.scalars().all()

    return {
        "pendentes": sum(1 for a in agendamentos if a.status == "Pendente"),
        "concluidos": sum(1 for a in agendamentos if a.status == "Concluído"),
        "ultimo_agendamento": max((a.data for a in agendamentos), default="Nenhum agendamento encontrado")
    }