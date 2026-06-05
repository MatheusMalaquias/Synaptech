"""
Ponto de entrada do ERP — FastAPI application.
Configura CORS, routers, lifespan e handlers de erro globais.
"""
import asyncio
from contextlib import asynccontextmanager

from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import get_settings
from app.core.redis import close_redis

settings = get_settings()

_worker_task = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicialização e shutdown da aplicação."""
    global _worker_task
    # Startup: inicia o worker de webhooks em background
    from app.integrations.n8n.webhook_worker import executar_worker
    _worker_task = asyncio.create_task(executar_worker())

    yield

    # Shutdown: cancela o worker e fecha Redis
    if _worker_task:
        _worker_task.cancel()
    await close_redis()


app = FastAPI(
    title="ERP FLV — API",
    description=(
        "Sistema ERP para substituição gradual do Fantastsoft FantastPDV. "
        "Fase 1: Auth, Produtos, Estoque, Webhooks. "
        "Fase 2: Caixa, Vendas, Integração n8n."
    ),
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    default_response_class=JSONResponse,
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
from app.api.v1.routes import (  # noqa: E402
    auth, caixa, estoque, n8n_integration, produtos, vendas, webhooks,
)

API_PREFIX = "/api/v1"

app.include_router(auth.router,            prefix=API_PREFIX + "/auth",     tags=["Auth"])
app.include_router(produtos.router,        prefix=API_PREFIX + "/produtos",  tags=["Produtos"])
app.include_router(estoque.router,         prefix=API_PREFIX + "/estoque",   tags=["Estoque"])
app.include_router(caixa.router,           prefix=API_PREFIX + "/caixa",     tags=["Caixa"])
app.include_router(vendas.router,          prefix=API_PREFIX + "/vendas",    tags=["Vendas"])
app.include_router(webhooks.router,        prefix=API_PREFIX + "/webhooks",  tags=["Webhooks"])
app.include_router(n8n_integration.router, prefix=API_PREFIX + "/n8n",      tags=["Integração n8n"])


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"], summary="Health check")
async def health_check():
    """Retorna status da aplicação. Usado pelo Docker healthcheck e load balancer."""
    return {"status": "ok", "version": app.version}


# ── Frontend PDV (servido como arquivo estático) ──────────────────────────────
_STATIC = Path(__file__).parent / "static"

@app.get("/", include_in_schema=False)
async def frontend():
    """Serve o PDV frontend."""
    return FileResponse(_STATIC / "index.html")


# Monta arquivos estáticos adicionais (css/js externos se necessário)
if _STATIC.exists():
    app.mount("/static", StaticFiles(directory=str(_STATIC)), name="static")


# ── Handler de erros global ───────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Captura erros não tratados e retorna resposta padronizada."""
    # Nunca expor detalhes internos em produção
    if settings.DEBUG:
        detail = str(exc)
    else:
        detail = "Erro interno do servidor"

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": detail, "code": "INTERNAL_ERROR"},
    )
