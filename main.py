import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import date

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

URL = os.getenv("SUPABASE_URL","").strip().strip('"').strip("'")
KEY = os.getenv("SUPABASE_KEY","").strip().strip('"').strip("'")

supabase=None
try:
    if URL.startswith("https://"):
        from supabase import create_client
        supabase=create_client(URL, KEY)
        print("Supabase OK")
except Exception as e:
    print("WARN Supabase:", e)

class Compra(BaseModel):
    data: date; fornecedor: str; documento: str|None=None; valor: float
    status: str="A Pagar"; categoria: str|None=None; forma_pagamento: str|None=None
    centro_custo: str|None=None; observacao: str|None=None

@app.get("/api")
def api_ok(): return {"ok": True, "supabase": bool(supabase)}

@app.get("/compras")
def listar():
    if not supabase: return []
    return supabase.table("compras_mbp").select("*").order("data",desc=True).execute().data

@app.post("/compras")
def criar(c: Compra):
    d=c.model_dump(); d["data"]=str(d["data"])
    return supabase.table("compras_mbp").insert(d).execute().data[0]

@app.get("/")
def home():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"status":"API no ar, index.html nao encontrado no servidor"}