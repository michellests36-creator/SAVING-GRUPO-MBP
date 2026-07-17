import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

URL = os.getenv("SUPABASE_URL","").strip().strip('"').strip("'")
KEY = os.getenv("SUPABASE_KEY","").strip().strip('"').strip("'")
from supabase import create_client
supabase = create_client(URL, KEY)

class CompraIn(BaseModel):
    data: str
    fornecedor: str
    descricao_material: str
    valor_inicial: float
    desconto: float = 0
    valor_final: float
    centro_custo_codigo: str
    centro_custo_nome: str
    comprador: str
    observacao: Optional[str] = ""
    documento: Optional[str] = ""

@app.get("/compras")
def listar():
    rows = supabase.table("compras").select("*").order("data", desc=True).execute().data
    out=[]
    for r in rows:
        out.append({
            "data": r.get("data"),
            "fornecedor": r.get("fornecedor"),
            "centro_custo_codigo": r.get("centro_custo_codigo") or "1410",
            "descricao_material": r.get("descricao_material") or r.get("observacao") or "",
            "comprador": r.get("comprador") or "Michelle",
            "valor_final": r.get("valor_final") or r.get("valor") or 0,
            "valor": r.get("valor") or 0
        })
    return out

@app.post("/compras")
def criar(c: CompraIn):
    payload = {
        "data": c.data,
        "fornecedor": c.fornecedor,
        "valor": float(c.valor_final),
        "status": "Lançado",
        "observacao": f"{c.descricao_material} | CENTRO:{c.centro_custo_codigo} | COMPRADOR:{c.comprador} | INI:{c.valor_inicial} DESC:{c.desconto} FINAL:{c.valor_final}"
    }
    result = supabase.table("compras").insert(payload).execute()
    return result.data[0]

@app.get("/")
def home():
    return FileResponse("index.html")