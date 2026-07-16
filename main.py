from fastapi import FastAPI
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="SAVING GRUPO MBP API")

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

@app.get("/")
def read_root():
    return {"status": "API SAVING GRUPO MBP no ar!", "supabase": "conectado"}

@app.get("/health")
def health_check():
    try:
        data = supabase.table("_dummy").select("*").limit(1).execute()
        return {"status": "ok", "db": "conectado"}
    except Exception as e:
        return {"status": "ok", "db": "erro esperado se tabela nao existe", "detalhe": str(e)}