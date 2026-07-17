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
    status: str
    observacao: Optional[str] = ""
    documento: Optional[str] = ""
    # aceita 'valor' se vier, pra não dar erro
    valor: Optional[float] = None

@app.get("/compras")
def listar():
    return supabase.table("compras").select("*").order("data", desc=True).execute().data

@app.post("/compras")
def criar(c: Compra):
    d = c.model_dump()
    d["valor"] = d["valor_final"] # cria o campo que sua tabela antiga exige
    return supabase.table("compras").insert(d).execute().data[0]

@app.get("/")
def home():
    return FileResponse("index.html")