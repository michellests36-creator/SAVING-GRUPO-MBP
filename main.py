import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
import traceback

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

URL = os.getenv("SUPABASE_URL","").strip().strip('"').strip("'")
KEY = os.getenv("SUPABASE_KEY","").strip().strip('"').strip("'")
from supabase import create_client
supabase = create_client(URL, KEY)

class CompraIn(BaseModel):
    data: str
    fornecedor: str
    descricao_material: Optional[str] = ""
    descricao: Optional[str] = ""
    valor_inicial: float = 0
    desconto: float = 0
    valor_final: float = 0
    total: float = 0
    centro_custo_codigo: Optional[str] = "1410"
    codigo_centro: Optional[str] = "1410"
    centro_custo_nome: Optional[str] = "1410 - MBP RJ"
    centro_de_custo: Optional[str] = "1410 - MBP RJ"
    comprador: str = "Michelle"
    observacao: Optional[str] = ""
    documento: Optional[str] = ""

@app.get("/compras")
def listar():
    try:
        rows = supabase.table("compras").select("*").order("data", desc=True).limit(100).execute().data
        return rows
    except Exception as e:
        return JSONResponse(status_code=200, content=[])

@app.post("/compras")
def criar(c: CompraIn):
    try:
        d = c.model_dump()
        desc_final = d.get("descricao_material") or d.get("descricao") or ""
        centro_cod = d.get("centro_custo_codigo") or d.get("codigo_centro") or "1410"
        centro_nome = d.get("centro_custo_nome") or d.get("centro_de_custo") or ""
        comprador = d.get("comprador") or "Michelle"
        v_final = d.get("valor_final") or d.get("total") or d.get("valor_inicial") or 0

        # Payload MINIMO que sua tabela compras COM CERTEZA tem
        payload = {
            "data": d.get("data"),
            "fornecedor": d.get("fornecedor"),
            "valor": float(v_final),
            "status": "Lançado",
            "observacao": f"{desc_final} | CENTRO:{centro_cod} {centro_nome} | COMP:{comprador} | INI:{d.get('valor_inicial')} DESC:{d.get('desconto')} | OBS:{d.get('observacao')} DOC:{d.get('documento')}"
        }
        res = supabase.table("compras").insert(payload).execute()
        return res.data[0]
    except Exception as e:
        print(traceback.format_exc())
        return JSONResponse(status_code=400, content={"erro": str(e), "detalhe": traceback.format_exc()})

@app.get("/")
def home():
    return FileResponse("index.html")