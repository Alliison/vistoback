from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, users, agenda, inspecoes, cameras, veiculos, relatorios
from app.database import async_engine as engine, Base  # ✅ Agora `engine` aponta para `async_engine`

app = FastAPI()

# Configuração do middleware CORS (corrigido especificamente para sua origem)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
	"http://vistotrack.com",
	"https://vistotrack.com",
	"http://www.vistotrack.com",
	"https://www.vistotrack.com"
	],  # Origem exata do seu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Criação das tabelas no banco ao iniciar
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        # pass
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)  # 🔹 Adicionando checkfirst=True

# Inclusão das rotas existentes
app.include_router(auth.router, prefix="/api", tags=["Auth"])
app.include_router(users.router, prefix="/api", tags=["Users"])
app.include_router(agenda.router, prefix="/api", tags=["Agenda"])
app.include_router(inspecoes.router, prefix="/api", tags=["Inspeções"])
app.include_router(cameras.router, prefix="/api", tags=["Câmeras"])
app.include_router(veiculos.router, prefix="/api", tags=["Veículos"])	
app.include_router(relatorios.router, prefix="/api", tags=["Relatórios"])	

@app.get("/ping")
async def ping():
    return {"message": "API VistoTrack está online!"}

