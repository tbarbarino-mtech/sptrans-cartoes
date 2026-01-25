import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.presentation.controllers import cartao_controller

app = FastAPI(
    title="SPTrans Golden Record API",
    description="API de consulta de cartões unificada e performática.",
    version="1.0.0"
)

# 1. Segurança: Configuração de CORS (Etapa 6)
origins = [
    "http://localhost",
    "http://localhost:3000", # Exemplo de frontend React/Vue
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET"], # Restringe verbos perigosos
    allow_headers=["*"],
)

# 2. Registra as Rotas
app.include_router(cartao_controller.router)

@app.get("/health")
def health_check():
    return {"status": "operational", "db": "connected"}

# Permite rodar via `python src/main.py`
if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)