# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.engine.rules import FanoronaGame

app = FastAPI()

# 1. Gérer les CORS pour autoriser le frontend à discuter avec l'API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En développement, on autorise toutes les origines
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instance globale du match en cours
game = FanoronaGame()

# 2. Route pour réinitialiser le jeu (appelée par startNewGame dans app.js)
@app.post("/api/reset")
def reset_game():
    global game
    game = FanoronaGame() # On écrase l'ancienne partie par une nouvelle
    return game.get_game_state()

# 3. Ta route existante pour jouer un coup
@app.post("/api/move")
def play_action(action_type: str, from_pos: int = None, to_pos: int = None):
    success = game.play_turn(action_type, from_pos, to_pos)
    return {"success": success, "state": game.get_game_state()}
