from fastapi import FastAPI
from supabase import create_client
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from datetime import datetime

load_dotenv()
app = FastAPI(title="API Compras MBP")

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

class Compra(BaseModel):
    centro: str = "MBP RJ"
    mes: str
    tot_inicial: float
    tot_desc: float
    numero_mes: int
    ano: int
    usuario_id: str = "default"

@app.get("/")
def home():
    return {"status": "API Compras MBP no ar"}

@app.post("/compras/criar")
def criar(dados: Compra):
    valor = dados.tot_inicial - dados.tot_desc
    r = supabase.table("compras_mbp").insert({
        "centro": dados.centro,
        "mes": dados.mes,
        "tot_inicial": dados.tot_inicial,git commit -m "fix requirements limpo"
        "tot_desc": dados.tot_desc,
        "valor": valor,
        "numero_mes": dados.numero_mes,
        "ano": dados.ano,
        "usuario_id": dados.usuario_id
    }).execute()
    return r.data[0]

@app.get("/compras")
def listar():
    r = supabase.table("compras_mbp").select("*").order("id", desc=True).execute()
    return r.data
