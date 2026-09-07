import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from sqlalchemy import text

from src.core.config import config
from src.api.db.database import engine, AsyncSessionLocal, dispose_engine
from src.api.routes import filtros, indicadores

# Configuração de logging estruturado para produção
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("vigitel.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerenciador de Ciclo de Vida (Lifespan) da aplicação FastAPI.
    - No startup: realiza o aquecimento (warm-up) e teste de conexão do pool PostgreSQL.
    - No shutdown: libera graciosamente todas as conexões ativas do pool.
    """
    logger.info("Iniciando VIGITEL Analytics API...")
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Conexão com PostgreSQL estabelecida com sucesso.")
    except Exception as exc:
        logger.error(f"Falha ao conectar ao PostgreSQL na inicialização: {exc}")

    yield

    logger.info("Encerrando VIGITEL Analytics API e liberando pool de conexões...")
    await dispose_engine()
    logger.info("Pool de conexões descartado com sucesso.")


app = FastAPI(
    title="VIGITEL Analytics API",
    description="API RESTful de alta performance para alimentar o dashboard epidemiológico de atividade física e sedentarismo baseado nos dados do VIGITEL (2006-2024).",
    version="1.0.0",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

# ─── Middlewares de Produção ──────────────────────────────────────────────────

# 1. Compressão automática GZip para payloads >= 1KB (reduz latência de rede no front-end)
app.add_middleware(GZipMiddleware, minimum_size=1024)

# 2. CORS (Cross-Origin Resource Sharing) com origens configuráveis via ambiente
is_wildcard = config.CORS_ORIGINS == ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=not is_wildcard,
    allow_methods=["GET", "HEAD", "OPTIONS"],
    allow_headers=["*"],
)


# 3. Observabilidade: Injeção do tempo de processamento da requisição no cabeçalho HTTP
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = (time.perf_counter() - start_time) * 1000
    response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
    return response


# 4. Cache HTTP para Edge / CDN: orienta navegadores e CDNs (Cloudflare/CloudFront/Vercel)
# a reaproveitarem respostas analíticas bem-sucedidas (GET 200) de inquéritos históricos estáticos.
@app.middleware("http")
async def add_cache_control_header(request: Request, call_next):
    response = await call_next(request)
    if request.method in ("GET", "HEAD") and response.status_code == 200:
        path = request.url.path
        if path.startswith("/api/v1/indicadores") or path.startswith("/api/v1/filtros"):
            response.headers["Cache-Control"] = (
                "public, max-age=3600, s-maxage=86400, stale-while-revalidate=86400"
            )
        elif path == "/health":
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


# ─── Tratamento Global de Exceções Não Tratadas (Segurança OWASP) ─────────────


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Erro não tratado na rota {request.url.path}: {exc}")
    return ORJSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "detail": "Ocorreu um erro interno no servidor ao processar a requisição.",
        },
    )


# ─── Registro dos Sub-roteadores ──────────────────────────────────────────────

app.include_router(filtros.router, prefix="/api/v1/filtros", tags=["Filtros"])
app.include_router(indicadores.router, prefix="/api/v1/indicadores", tags=["Indicadores"])

# ─── Health Check Endpoint (Liveness / Readiness Probe) ───────────────────────


@app.api_route(
    "/health", methods=["GET", "HEAD"], tags=["Sistema"], summary="Health Check da Aplicação"
)
async def health_check():
    """
    Endpoint de verificação de disponibilidade operacional da API e conectividade com o banco de dados.
    Utilizado por orquestradores (Docker, Kubernetes, AWS/GCP ALB) para health check.
    """
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected", "version": "1.0.0"}
    except Exception as exc:
        logger.error(f"Health check falhou ao contatar o PostgreSQL: {exc}")
        return ORJSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "degraded",
                "database": "disconnected",
                "version": "1.0.0",
                "error": "Banco de dados inacessível",
            },
        )
