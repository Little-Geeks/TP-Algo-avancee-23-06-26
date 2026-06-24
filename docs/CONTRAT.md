# CONTRAT Phase 0 — Fanoron-telo

> **Source de vérité** : `backend/app/engine/state.py` est le code de référence.
> Ce document l'explique et fige les signatures des fonctions à implémenter.
> **Toute modification doit être validée par les 3 membres.**

---

## 1. Convention de numérotation du plateau

Index des bits (LSB = case 0, bitboard = entier 9 bits) :

```
Plateau visuel :           Index des bits :

    0 --- 1 --- 2              bit 0 | bit 1 | bit 2
    |  \  |  /  |              ------+-------+------
    |   \ | /   |              bit 3 | bit 4 | bit 5
    3 --- 4 --- 5              ------+-------+------
    |   / | \   |              bit 6 | bit 7 | bit 8
    |  /  |  \  |
    6 --- 7 --- 8
```

- **Bitboard** : entier 9 bits, bit `i` = 1 si un pion occupe la case `i`.
- **Topologie** : les diagonales passent uniquement par le **centre (case 4)**.
  - Coins `(0, 2, 6, 8)` : 3 voisins chacun
  - Bords `(1, 3, 5, 7)` : 3 voisins chacun
  - Centre `(4)` : 8 voisins

Les masques corrigés (`backend/app/engine/board.py`) :
- `WINNING_MASKS` : 8 alignements (3 lignes + 3 colonnes + 2 diagonales).
- `ADJACENT_MASKS` : voisins de chaque case (déjà corrects).

---

## 2. État du jeu : `GameState`

**Fichier** : `backend/app/engine/state.py` — **déjà implémenté en Phase 0.**

| Champ | Type | Description |
|---|---|---|
| `phase` | `Phase` | `1` = PLACEMENT, `2` = MOVEMENT |
| `turn` | `Player` | `1` ou `2` — joueur qui doit jouer |
| `p1_bb` | `int` | Bitboard J1 (9 bits) |
| `p2_bb` | `int` | Bitboard J2 (9 bits) |
| `p1_to_place` | `int` | Pions restant à poser pour J1 (Phase 1) |
| `p2_to_place` | `int` | Idem J2 |
| `winner` | `Player` | `0` = NONE (en cours / nul), `1` ou `2` sinon |
| `is_over` | `bool` | `True` si partie terminée |
| `move_count` | `int` | Nombre d'actions jouées |

**Propriétés clés** :
- `frozen=True` → **immuable** (un nouvel état à chaque action)
- **hashable** → utilisable comme clé dans la table de transposition de l'IA
- `state.to_dict()` → version JSON-friendly pour l'API

### Représentation JSON (échangée API ↔ Frontend)

```json
{
  "phase": 1,
  "turn": 1,
  "p1_bb": 17,
  "p2_bb": 2,
  "p1_positions": [0, 4],
  "p2_positions": [1],
  "p1_to_place": 1,
  "p2_to_place": 2,
  "winner": 0,
  "is_over": false,
  "move_count": 3
}
```

---

## 3. Action : `Action`

**Fichier** : `backend/app/engine/state.py` — **déjà implémenté en Phase 0.**

```python
Action(type=Phase.PLACEMENT, dst=4)              # Phase 1 : pose en case 4
Action(type=Phase.MOVEMENT, src=0, dst=1)        # Phase 2 : déplacement 0 -> 1
```

Règles de validation (déjà codées dans `__post_init__`) :
- `0 <= dst <= 8`
- En PLACEMENT : `src` doit être `None`
- En MOVEMENT : `src` est obligatoire et `0 <= src <= 8`

---

## 4. Signatures — À IMPLÉMENTER

### 🅰️ Personne A — `backend/app/engine/rules.py`

```python
from app.engine.state import GameState, Action, Player, Phase

def get_legal_actions(state: GameState) -> list[Action]:
    """Toutes les actions légales pour le joueur `state.turn`."""

def apply_action(state: GameState, action: Action) -> GameState:
    """
    Applique `action` à `state`. Renvoie un NOUVEL état (immuable).
    - Met à jour le bitboard du joueur
    - Décrémente *_to_place si PLACEMENT
    - Alterne `turn`
    - Passe en Phase MOVEMENT quand les 6 pions sont posés
    - Calcule winner / is_over (victoire immédiate en PLACEMENT)
    - Incrémente move_count
    Lève ValueError si l'action est illégale.
    """

def is_valid_action(state: GameState, action: Action) -> bool:
    """True si `action` est légale dans `state` (sans lever d'exception)."""

def is_game_over(state: GameState) -> bool:
    """True si la partie est terminée."""

def get_winner(state: GameState) -> Player:
    """
    Player.ONE / TWO si victoire par alignement.
    Player.NONE si nul ou partie en cours.
    """

def is_draw(state: GameState) -> bool:
    """True si plus aucune action légale sans gagnant (blocage / répétition)."""
```

**Règles à respecter (rappel du sujet)** :
- Phase 1 : à tour de rôle, chaque joueur pose 1 pion sur une case libre.
  - **Victoire immédiate** dès qu'un joueur aligne ses 3 pions pendant cette phase.
- Phase 2 : après les 6 poses, chaque joueur déplace 1 de ses pions vers une
  case **adjacente libre** (selon `ADJACENT_MASKS`).
  - Victoire dès qu'un joueur aligne ses 3 pions.
- Match nul : à définir (ex. `move_count > 100` sans gagnant, ou plus propre :
  détection de cycle via l'historique géré par l'API).

---

### 🅱️ Personne B — `backend/app/ai/`

#### `evaluation.py`

```python
from app.engine.state import GameState, Player

def evaluate(state: GameState, player: Player) -> int:
    """
    Score statique du `state` du point de vue de `player`.
    Convention :
      - score > 0  -> `player` est avantagé
      - score < 0  -> `player` est désavantagé
      - score = 0  -> équilibré
    Doit être symétrique : evaluate(s, A) == -evaluate(s_symétrique, A).

    Pistes : nb d'alignements ouverts à 2 pions, contrôle du centre (case 4),
    mobilité (nb de déplacements légaux), menaces immédiates.
    """
```

#### `minimax.py`

```python
from app.engine.state import GameState, Action, Player

def best_move(
    state: GameState,
    difficulty: str,           # "easy" | "medium" | "hard"
    player: Player,
) -> Action | None:
    """
    Retourne la meilleure Action pour `player` dans `state`, ou None si la
    partie est terminée.

    Niveaux :
      - "easy"   : profondeur 1 + bruit aléatoire (souvent sous-optimale)
      - "medium" : profondeur 4, alpha-bêta pur
      - "hard"   : profondeur >= 6, alpha-bêta + table de transposition
                   + opening book + iterative deepening avec timeout
    """
```

#### `opening_book.py`

```python
from app.engine.state import GameState, Action

def get_opening_move(state: GameState) -> Action | None:
    """Renvoie un coup d'ouverture si `state` correspond à un état connu,
    sinon None (l'IA tombe alors sur Minimax)."""
```

---

### 🅲 Personne C — `backend/app/main.py` (API FastAPI)

#### Endpoints

| Méthode | Route | Corps (JSON) | Réponse |
|---|---|---|---|
| `GET`  | `/` | — | Health check |
| `POST` | `/new-game` | `{"mode": "HvH"\|"HvIA"\|"IvIA", "difficulty": "easy"\|"medium"\|"hard", "ai_starts": bool}` | `{"session_id": str, "state": {...}}` |
| `POST` | `/move` | `{"session_id": str, "action": {"type": 1\|2, "src": int\|null, "dst": int}}` | `{"state": {...}, "legal_actions": [...], "winner": 0\|1\|2}` |
| `POST` | `/ai-move` | `{"session_id": str}` | `{"state": {...}, "action": {...}, "winner": 0\|1\|2}` |
| `POST` | `/undo` | `{"session_id": str}` | `{"state": {...}, "undone": bool}` |
| `POST` | `/redo` | `{"session_id": str}` | `{"state": {...}, "redone": bool}` |
| `GET`  | `/legal-actions/{session_id}` | — | `{"actions": [...]}` |

#### Session (en mémoire, dict global pour le hackathon)

```python
sessions: dict[str, dict] = {}  # session_id -> {"state": GameState, "mode": ..., "history": [...], "redo_stack": [...]}
```

- **Undo/Redo** : `history` = pile des états précédents ; `redo_stack` = pile des états annulés.
- En mode HvIA, après un `/move` humain, l'API doit enchaîner automatiquement le coup de l'IA
  **OU** laisser le frontend appeler `/ai-move` (au choix — à décider ensemble).

#### Pydantic schemas (à créer dans `backend/app/schemas.py`)

```python
class ActionIn(BaseModel):
    type: int                # 1 ou 2
    src: int | None = None
    dst: int

class MoveRequest(BaseModel):
    session_id: str
    action: ActionIn

class NewGameRequest(BaseModel):
    mode: Literal["HvH", "HvIA", "IvIA"] = "HvH"
    difficulty: Literal["easy", "medium", "hard"] = "medium"
    ai_starts: bool = False
```

---

## 5. Points d'intégration (dependencies entre A, B, C)

```
                      ┌──────────────────────────────┐
                      │  state.py  (CONTRAT, figé)   │
                      └──────────────┬───────────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              ▼                      ▼                      ▼
      ┌──────────────┐       ┌──────────────┐       ┌──────────────┐
      │  rules.py    │       │  minimax.py  │       │   main.py    │
      │   (A)        │       │   (B)        │       │    (C)       │
      │              │       │              │       │              │
      │ get_legal_   │◄──────┤ expand via   │◄──────┤ appelle      │
      │   actions    │       │ rules        │       │ best_move    │
      │ apply_action │       │              │       │ apply_action │
      │ is_over      │──────►│              │──────►│              │
      │ winner       │       │              │       │              │
      └──────────────┘       └──────────────┘       └──────────────┘
              │                                              │
              └─────────────────► board.py ◄─────────────────┘
                                (masques bitboard)
```

**Dépendances bloquantes** :
1. **B a besoin de** `rules.get_legal_actions(state)` et `rules.apply_action(state, action)` pour le Minimax.
   → A doit livrer ces 2 fonctions en priorité.
2. **C a besoin de** Toutes les fonctions de A + `best_move` de B pour les endpoints.
3. **B et A** partagent la convention des bitboards → d'où la correction de `board.py` en Phase 0.

---

## 6. Décisions verrouillées

### ✅ Q1 — Gestion des tours en mode IA vs IA → **option b**
Le frontend appelle `/ai-move` à intervalle régulier (animations visibles, démo interactive).
*Implémenté par Personne C (API + Frontend).*

### ✅ Q2 — Match nul automatique → **option a**
`move_count > 50` en Phase 2 → `is_over=True, winner=NONE`.
*Implémenté dans `app/engine/rules.py::_DRAW_MOVE_LIMIT = 50`.*

### ✅ Q3 — En mode HvIA, qui est le Joueur 1 ? → **option b**
Configurable via `ai_starts: bool` à la création de la partie.
*À implémenter dans Personne C (`/new-game` endpoint).*

### ✅ Q4 — Profondeurs exactes par difficulté → **verrouillé**
Implémenté dans `app/ai/minimax.py::_DIFFICULTY` :

| Difficulté | Profondeur | Alpha-Beta | Transposition | Iterative Deepening | Bruit aléatoire |
|---|---|---|---|---|---|
| `easy`   | 2 (fixe) | ✅ | ❌ | ❌ | 30 % |
| `medium` | 4 (fixe) | ✅ | ✅ | ❌ | 0 % |
| `hard`   | 1→20 (jusqu'à timeout 2.0s) | ✅ | ✅ | ✅ | 0 % |

Performances mesurées (backend/test_ai.py) :
- `medium` : ~20 ms / coup (largement sous 500 ms).
- `hard`   : ~900 ms / coup (sous le timeout 2 s).

### ✅ Q5 — Convention de score pour `evaluate` → **verrouillé**
Implémenté dans `app/ai/evaluation.py` :
- `WIN_SCORE = 1_000_000` (cf. `WIN_SCORE`).
- Victoire : `+WIN_SCORE + depth` (le `+depth` privilégie les victoires rapides dans Negamax).
- Défaite : `-WIN_SCORE - depth` (la défaite lointaine est moins mauvaise).
- Évaluation symétrique : `evaluate(s, P1) == -evaluate(s, P2)` pour tout état non terminal.

---

## 7. Vérification post-Phase 0

À la fin de la Phase 0, ce qui doit être vrai :
- [x] `board.py` corrigé et documenté
- [x] `state.py` implémente `GameState`, `Action`, `Phase`, `Player`
- [x] `engine/__init__.py` exporte le contrat
- [x] `docs/CONTRAT.md` présent
- [x] Les 5 questions de la section 6 sont tranchées et verrouillées
- [x] `python -c "from app.engine import GameState, Action, initial_state"` passe sans erreur

### Phase 1 — État au 24/06/2026 (Personne B — Lead IA)

✅ `app/engine/rules.py` — Implémentation de référence (transitions, terminalité, blocage, limite 50 coups).
✅ `app/ai/evaluation.py` — Fonction d'évaluation heuristique (menaces, centre, mobilité).
✅ `app/ai/minimax.py` — Negamax + alpha-bêta + table de transposition + iterative deepening.
✅ `app/ai/opening_book.py` — Bibliothèque d'ouvertures (centre puis coin opposé).
✅ `tests/test_ai.py` — 23 tests (règles, évaluation, IA, table, tournois, perfs).

Test runner : `cd backend && python -m pytest tests/ -v` → **23/23 passent en ~15s**.

Travail restant pour Personne A :
- Reprendre `app/engine/rules.py` (interface respectée, peut optimiser / remplacer).
- Ajouter tests spécifiques à l'engine (mouvement en Phase 2, blocage, etc.).

Travail restant pour Personne C :
- Endpoints FastAPI dans `app/main.py` (`/new-game`, `/move`, `/ai-move`, `/undo`, `/redo`).
- Frontend `frontend/{index.html,app.js,style.css}`.
- Déploiement (Dockerfile ou vercel.json / render.yaml).
- README sections 1-6.
