import os
import traceback

from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from supabase import create_client


# ===================================================
# CONFIGURAÇÃO DA API
# ===================================================

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


# ===================================================
# CONEXÃO COM O SUPABASE
# ===================================================

def init_supabase():

    url = os.getenv("SUPABASE_URL", "").strip().strip('"').strip("'")
    key = os.getenv("SUPABASE_KEY", "").strip().strip('"').strip("'")

    return create_client(url, key)


supabase = init_supabase()


# ===================================================
# MODELO DAS COMPRAS
# ===================================================

class CompraIn(BaseModel):

    data: str

    fornecedor: str

    descricao_material: str = ""

    valor_inicial: float = 0

    desconto: float = 0

    valor_final: float = 0

    centro_custo_codigo: str = ""

    centro_custo_nome: str = ""

    comprador: str = ""

    documento: Optional[str] = ""

    observacao: Optional[str] = ""


# ===================================================
# FUNÇÃO PARA INSERIR REGISTROS
# ===================================================

def inserir_registro(dados):

    try:

        supabase.table("compras").insert(dados).execute()

        return True, None

    except Exception as e:

        return False, str(e) + "\n" + traceback.format_exc()


# ===================================================
# LISTAR COMPRAS
# ===================================================

@app.get("/compras")
def listar():

    try:

        resposta = (
            supabase
            .table("compras")
            .select("*")
            .order("data", desc=True)
            .limit(100)
            .execute()
        )

        return resposta.data

    except Exception:

        return []


# ===================================================
# CADASTRAR COMPRA
# ===================================================

@app.post("/compras")
def criar(c: CompraIn):

    dados_novo_registro = {

        "data": c.data,

        "fornecedor": c.fornecedor.strip(),

        "descricao_material": c.descricao_material,

        "valor_inicial": c.valor_inicial,

        "desconto": c.desconto,

        "valor_final": c.valor_final,

        "centro_custo_codigo": c.centro_custo_codigo,

        "centro_custo_nome": c.centro_custo_nome,

        "comprador": c.comprador,

        "documento": c.documento,

        "observacao": c.observacao

    }

    ok, erro = inserir_registro(dados_novo_registro)

    if ok:

        return {
            "ok": True,
            "mensagem": "Compra cadastrada com sucesso."
        }

    return JSONResponse(
        status_code=400,
        content={
            "erro": erro,
            "payload_enviado": dados_novo_registro
        }
    )


# ===================================================
# PÁGINA INICIAL
# ===================================================

@app.get("/")
def home():

    return FileResponse("index.html")


# ===================================================
# DEBUG DA TABELA
# ===================================================

@app.get("/debug")
def debug():

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
                "exemplo": resposta.data
            }

        return {
            "mensagem": "Tabela vazia."
        }

    except Exception as e:

        return {
            "erro": str(e)
        }