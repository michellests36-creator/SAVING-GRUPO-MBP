import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import date
from typing import Optional
app=FastAPI()
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_methods=["*"],allow_headers=["*"])
URL=os.getenv("SUPABASE_URL","").strip().strip('"').strip("'")
KEY=os.getenv("SUPABASE_KEY","").strip().strip('"').strip("'")
supabase=None
try:
 from supabase import create_client
 if URL.startswith("https://"): supabase=create_client(URL,KEY)
except Exception as e: print(e)
class Compra(BaseModel):
 data:date; fornecedor:str; descricao_material:str; valor_inicial:float; desconto:float=0; valor_final:float
 centro_custo_codigo:str; centro_custo_nome:str; comprador:str; status:str="A Pagar"; documento:Optional[str]=None; observacao:Optional[str]=None
@app.get("/compras")
def listar(): return supabase.table("compras_mbp").select("*").order("data",desc=True).execute().data if supabase else []
@app.post("/compras")
def criar(c:Compra): d=c.model_dump(); d["data"]=str(d["data"]); return supabase.table("compras_mbp").insert(d).execute().data[0]
@app.get("/")
def home(): return FileResponse("index.html")