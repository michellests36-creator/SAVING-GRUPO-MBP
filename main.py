import logging
import os
import traceback
from datetime import date
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, field_validator
from supabase import Client, create_client

# ===================================================
# LOGGING
# ===================================================
# Erros ficam registrados no servidor (Render) mesmo quando
# não são expostos na resposta ao cliente.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("compras-api")


# ===================================================
# CONFIGURAÇÃO DA API
# ===================================================

app = FastAPI(title="Grupo MBP | Compras API")

# Em produção, prefira restringir allow_origins ao domínio do
# front-end (ex: ["https://seu-dominio.com"]) em vez de "*".
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Só devolve o traceback completo no corpo da resposta quando
# DEBUG=1 estiver definido no ambiente. Em produção, deixe desligado
# para não vazar detalhes internos (nomes de tabelas, stack trace etc).
DEBUG = os.getenv("DEBUG", "0") == "1"


# ===================================================
# CONEXÃO COM O SUPABASE
# ===================================================

def init_supabase() -> Client:
    url = os.getenv("SUPABASE_URL", "").strip().strip('"').strip("'")
    key = os.getenv("SUPABASE_KEY", "").strip().strip('"').strip("'")

    if not url or not key:
        raise RuntimeError(
            "SUPABASE_URL e/ou SUPABASE_KEY não configurados. "
            "Defina essas variáveis de ambiente antes de iniciar a API."
        )

    return create_client(url, key)


try:
    supabase = init_supabase()
except Exception:
    logger.exception("Falha ao inicializar o cliente Supabase")
    raise


# ===================================================
# MODELO DAS COMPRAS
# ===================================================

class CompraIn(BaseModel):
    data: str  # formato esperado: YYYY-MM-DD
    fornecedor: str = Field(..., min_length=1)
    descricao_material: str = ""
    valor_inicial: float = Field(default=0, ge=0)
    desconto: float = Field(default=0, ge=0)
    valor_final: float = Field(default=0, ge=0)
    centro_custo_codigo: str = ""
    centro_custo_nome: str = ""
    comprador: str = ""
    documento: Optional[str] = ""
    observacao: Optional[str] = ""

    @field_validator("data")
    @classmethod
    def validar_data(cls, v: str) -> str:
        try:
            date.fromisoformat(v)
        except ValueError:
            raise ValueError(
                "Campo 'data' inválido. Use o formato YYYY-MM-DD."
            )
        return v

    @field_validator("fornecedor")
    @classmethod
    def normalizar_fornecedor(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Campo 'fornecedor' não pode ficar em branco.")
        return v


# ===================================================
# FUNÇÃO PARA INSERIR REGISTROS
# ===================================================

def inserir_registro(dados: dict) -> tuple[bool, Optional[str]]:
    try:
        supabase.table("compras").insert(dados).execute()
        return True, None
    except Exception as e:
        logger.error("Erro ao inserir compra: %s", e)
        detalhe = str(e)
        if DEBUG:
            detalhe += "\n" + traceback.format_exc()
        return False, detalhe


# ===================================================
# LISTAR COMPRAS
# ===================================================

@app.get("/compras")
def listar(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    try:
        resposta = (
            supabase
            .table("compras")
            .select("*")
            .order("data", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )
        return resposta.data
    except Exception:
        logger.exception("Erro ao listar compras")
        # Mantém contrato original (lista vazia) para não quebrar o
        # front-end, mas o erro real fica registrado no log do servidor.
        return []


# ===================================================
# CADASTRAR COMPRA
# ===================================================

@app.post("/compras")
def criar(c: CompraIn):
    dados_novo_registro = {
        "data": c.data,
        "fornecedor": c.fornecedor,
        "descricao_material": c.descricao_material,
        "valor_inicial": c.valor_inicial,
        "desconto": c.desconto,
        "valor_final": c.valor_final,
        "centro_custo_codigo": c.centro_custo_codigo,
        "centro_custo_nome": c.centro_custo_nome,
        "comprador": c.comprador,
        "documento": c.documento,
        "observacao": c.observacao,
    }

    ok, erro = inserir_registro(dados_novo_registro)

    if ok:
        return {
            "ok": True,
            "mensagem": "Compra cadastrada com sucesso.",
        }

    # FORÇA a exibição do erro real retornado pelo Supabase na tela do navegador
    raise HTTPException(
        status_code=400,
        detail={"erro": "Erro ao salvar no banco", "detalhe_real": erro, "payload": dados_novo_registro}
    )

# ===================================================
# PÁGINA INICIAL
# ===================================================

@app.get("/")
def home():
    return FileResponse("index.html")


# ===================================================
# HEALTH CHECK
# ===================================================

@app.get("/health")
def health():
    """Endpoint simples para checagem de disponibilidade (uptime monitors etc)."""
    return {"status": "ok"}


# ===================================================
# DEBUG DA TABELA
# ===================================================

@app.get("/debug")
def debug():
    if not DEBUG:
        raise HTTPException(
            status_code=404,
            detail="Endpoint de debug desativado. Defina DEBUG=1 para habilitar.",
        )

    try:
        resposta = (
            supabase
            .table("compras")
            .select("*")
            .limit(1)
            .execute()
        )

        if resposta.data:
            return {
                "colunas": list(resposta.data[0].keys()),
                "exemplo": resposta.data,
            }

        return {"mensagem": "Tabela vazia."}

    except Exception as e:
        logger.exception("Erro no endpoint /debug")
        return {"erro": str(e)}