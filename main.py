```python
import os
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from supabase import create_client


# Cria a aplicação
app = FastAPI()

# Libera o acesso da API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variáveis do Supabase
URL = os.getenv("SUPABASE_URL", "").strip().strip('"').strip("'")
KEY = os.getenv("SUPABASE_KEY", "").strip().strip('"').strip("'")

# Conexão com o Supabase
supabase = create_client(URL, KEY)


# Modelo dos dados da compra
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


# Lista todas as compras
@app.get("/compras")
def listar():
    return (
        supabase
        .table("compras")
        .select("*")
        .order("data", desc=True)
        .execute()
        .data
    )


# Cadastra uma nova compra
@app.post("/compras")
def criar(c: Compra):
    dados = c.model_dump()

    return (
        supabase
        .table("compras")
        .insert(dados)
        .execute()
        .data[0]
    )


# Abre a página inicial
@app.get("/")
def home():
    return FileResponse("index.html")

