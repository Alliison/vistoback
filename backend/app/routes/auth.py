from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import User
from app.schemas import UserLogin, TokenResponse, UserCreate
from app.utils.security import verify_password, create_access_token, hash_password
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    print(f"Recebendo JSON: {user.dict()}")  # 🔹 Log dos dados recebidos

    stmt = select(User).where(User.email == user.email)
    existing_user = await db.execute(stmt)

    if existing_user.scalar():
        raise HTTPException(status_code=400, detail="Usuário já cadastrado")

    hashed_password = hash_password(user.senha)
    new_user = User(nome=user.nome, email=user.email, telefone=user.telefone, senha=hashed_password)

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return {"message": "Usuário registrado com sucesso"}


@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == user_data.email)
    result = await db.execute(stmt)
    existing_user = result.scalars().first()

    if not existing_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado")

    if not verify_password(user_data.senha, existing_user.senha):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Senha incorreta")

    access_token = create_access_token(
        data={"sub": existing_user.email}, 
        expires_delta=timedelta(minutes=30)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": existing_user.role  # 🔹 Adicionado para redirecionamento no frontend
    }
