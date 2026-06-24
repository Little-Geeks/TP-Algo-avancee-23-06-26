from fastapi import FastAPI

app = FastAPI(title="Fanorona Telo API")

@app.get("/")
def read_root():
    return {"status": "Le serveur du jeu Fanorona-Telo fonctionne correctement"}