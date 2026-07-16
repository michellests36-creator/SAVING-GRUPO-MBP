import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client
from dotenv import load_dotenv
from pydantic import BaseModel
from datetime import date

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Faltam SUPABASE_URL e SUPABASE_KEY no.env / Environment")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="SAVING GRUPO MBP - Compras API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Compra(BaseModel):
    data: date
    fornecedor: str
    documento: str | None = None
    valor: float
    status: str = "A Pagar"
    categoria: str | None = None
    forma_pagamento: str | None = None
    centro_custo: str | None = None
    observacao: str | None = None

@app.get("/")
def home():
    return {"status": "API MBP no ar", "docs": "/docs"}

@app.get("/compras")
def listar_compras():
    resp = supabase.table("compras_mbp").select("*").order("data", desc=True).execute()
    return resp.data

@app.post("/compras")
def criar_compra(compra: Compra):
    dados = compra.model_dump()
    dados["data"] = str(dados["data"])
    try:
        resp = supabase.table("compras_mbp").insert(dados).execute()
        return resp.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))