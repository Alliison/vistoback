from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import Relatorio
from app.schemas.relatorio import RelatorioCreate, RelatorioResponse
from app.utils.auth import get_current_user
from app.models.user import users
from datetime import date
from typing import Optional

router = APIRouter(prefix="/relatorios", tags=["Relatórios"])

@router.get("/", response_model=list[RelatorioResponse])
async def listar_relatorios(inspecao_id: Optional[int] = None, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    if inspecao_id:
        result = await db.execute(
            select(Relatorio).where(
                Relatorio.usuario_id == usuario.id,
                Relatorio.inspecao_id == inspecao_id
            )
        )
    else:
        result = await db.execute(
            select(Relatorio).where(Relatorio.usuario_id == usuario.id)
        )
    return result.scalars().all()

@router.get("/{relatorio_id}", response_model=RelatorioResponse)
async def obter_relatorio(relatorio_id: int, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    result = await db.execute(select(Relatorio).where(Relatorio.id == relatorio_id, Relatorio.usuario_id == usuario.id))
    relatorio = result.scalar_one_or_none()
    if not relatorio:
        raise HTTPException(status_code=404, detail="Relatório não encontrado")
    return relatorio

@router.post("/", response_model=RelatorioResponse, status_code=status.HTTP_201_CREATED)
async def criar_relatorio(dados: RelatorioCreate, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    novo = Relatorio(
        veiculo_id=dados.veiculo_id,
        usuario_id=usuario.id,
        inspecao_id=dados.inspecao_id,
        data=dados.data or date.today(),
        resultado=dados.resultado,
        arquivo_pdf=dados.arquivo_pdf
    )
    db.add(novo)
    await db.commit()
    await db.refresh(novo)
    return novo
