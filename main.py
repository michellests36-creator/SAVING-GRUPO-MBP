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
from supabase import create_client
supabase = create_client(URL, KEY)

class Compra(BaseModel):
    data: str
    fornecedor: str
    valor: float
    status: str
    # vou salvar tudo que é novo dentro da observação pra não precisar criar coluna
    observacao: str

@app.get("/compras")
def listar():
    return supabase.table("compras").select("*").order("data", desc=True).execute().data

@app.post("/compras")
def criar(c: Compra):
    return supabase.table("compras").insert(c.model_dump()).execute().data[0]

@app.get("/")
def home():
    return FileResponse("index.html")