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

class Compra(BaseModel):
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
    return supabase.table("compras").select("*").order("data", desc=True).execute().data

@app.post("/compras")
def criar(c: Compra):
    d = c.model_dump()
    d["valor"] = d["valor_final"]
    d["status"] = "Lançado" # só pra não quebrar sua tabela antiga que exige status
    try:
        return supabase.table("compras").insert(d).execute().data[0]
    except:
        simples = {
            "data": d["data"],
            "fornecedor": d["fornecedor"],
            "valor": d["valor_final"],
            "status": "Lançado",
            "observacao": f"{d['descricao_material']} | {d['centro_custo_codigo']} | {d['comprador']}"
        }
        return supabase.table("compras").insert(simples).execute().data[0]

@app.get("/")
def home():
    return FileResponse("index.html")