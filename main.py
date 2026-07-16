import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client
from pydantic import BaseModel
from datetime import date

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="SAVING GRUPO MBP")

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
    return {"status": "API MBP no ar - OK", "supabase_ok": bool(supabase)}

@app.get("/compras")
def listar():
    if not supabase:
        raise HTTPException(500, "Supabase não configurado no Render Environment")
    return supabase.table("compras_mbp").select("*").order("data", desc=True).execute().data

@app.post("/compras")
def criar(c: Compra):
    if not supabase:
        raise HTTPException(500, "Supabase não configurado")
    d = c.model_dump()
    d["data"] = str(d["data"])
    return supabase.table("compras_mbp").insert(d).execute().data[0]