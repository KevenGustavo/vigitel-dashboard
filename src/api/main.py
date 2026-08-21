from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import filtros, indicadores

app = FastAPI(
    title="VIGITEL Analytics API",
    description="API RESTful para alimentar o dashboard de indicadores de atividade física e sedentarismo baseado nos dados do VIGITEL (2006-2024).",
    version="1.0.0",
)

# Configuração de CORS (Cross-Origin Resource Sharing)
# Permite que o frontend (Tailwind/React/Vanilla JS) em outra porta ou domínio consuma a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, substituir pelos domínios reais do frontend
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

# Registro dos sub-roteadores
app.include_router(filtros.router, prefix="/api/v1/filtros", tags=["Filtros"])
app.include_router(indicadores.router, prefix="/api/v1/indicadores", tags=["Indicadores"])

@app.get("/health", tags=["Sistema"])
async def health_check():
    """Endpoint básico para verificação de disponibilidade (Health Check)"""
    return {"status": "ok", "message": "API está no ar"}
