import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
import traceback
from supabase import create_client

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# IGUAL SEU CODIGO STREAMLIT
def init_supabase():
    url = os.getenv("SUPABASE_URL","").strip().strip('"').strip("'")
    key = os.getenv("SUPABASE_KEY","").strip().strip('"').strip("'")
    return create_client(url, key)

supabase = init_supabase()

class CompraIn(BaseModel):
    data: str
    fornecedor: str
    descricao_material: str = ""
    valor_inicial: float = 0
    desconto: float = 0
    valor_final: float = 0
    centro_custo_codigo: str = "1410"
    centro_custo_nome: str = "1410 - MBP RJ"
    comprador: str = "Michelle"
    observacao: Optional[str] = ""
    documento: Optional[str] = ""

def inserir_registro(dados_dict):
    # MESMA FUNCAO DO SEU STREAMLIT
    try:
        supabase.table('compras').insert(dados_dict).execute()
        return True, None
    except Exception as e:
        return False, str(e) + "\n" + traceback.format_exc()

@app.get("/compras")
def listar():
    try:
        r = supabase.table('compras').select("*").order("data", desc=True).limit(100).execute()
        return r.data
    except Exception as e:
        return []

@app.post("/compras")
def criar(c: CompraIn):
    # MONTA IGUAL VOCÊ FEZ NO CADASTRO DE FORNECEDORES
    # Só usa colunas que EXISTEM na tabela compras: data, fornecedor, valor, status, observacao
    dados_novo_registro = {
        "data": c.data,
        "fornecedor": c.fornecedor.strip(),
        "valor": float(c.valor_final or 0),
        "status": "Lançado",
        "observacao": f"{c.descricao_material} | CENTRO:{c.centro_custo_codigo}-{c.centro_custo_nome} | COMPRADOR:{c.comprador} | INI:{c.valor_inicial} DESC:{c.desconto} FINAL:{c.valor_final} | OBS:{c.observacao} DOC:{c.documento}"
    }

    ok, erro = inserir_registro(dados_novo_registro)
    if ok:
        return {"ok": True}
    else:
        # AQUI NÃO VAI MAIS DAR INTERNAL SERVER ERROR
        # Vai te mostrar o erro real na tela
        return JSONResponse(status_code=400, content={"erro": erro, "payload_enviado": dados_novo_registro})

@app.get("/")
def home():
    return FileResponse("index.html")

@app.get("/debug")
def debug():
    try:
        r = supabase.table('compras').select("*").limit(1).execute()
        return {"colunas_existentes": list(r.data[0].keys()) if r.data else "tabela vazia", "exemplo": r.data}
    except Exception as e:
        return {"erro_debug": str(e)}