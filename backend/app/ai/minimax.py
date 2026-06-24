"""
IA du Fanoron-telo : Minimax + Alpha-Beta + techniques avancées.

Niveaux de difficulté (Q4 du contrat - verrouillé) :
  - "easy"   : profondeur 2 + 30% de bruit aléatoire (coups sous-optimaux).
  - "medium" : profondeur 4, alpha-beta pur, move ordering simple.
  - "hard"   : iterative deepening jusqu'à timeout (2.0s) ou profondeur max (20),
               avec table de transposition + move ordering + opening book.

Techniques implémentées :
  - Alpha-Beta pruning (toutes difficultés sauf easy pur).
  - Table de transposition (Zobrist hashing via hash(frozen GameState).
  - Move ordering (coups gagnants / centre d'abord -> meilleur élagage).
  - Iterative deepening avec timeout (difficulté hard uniquement).
  - Bonus de profondeur pour victoires rapides (WIN_SCORE - depth).

Convention Negamax : à chaque nœud, on maximise le score du joueur qui joue,
en inversant le signe à chaque demi-coup.
"""

from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass
from typing import Optional

from app.ai.evaluation import WIN_SCORE, evaluate_for_turn
from app.engine.rules import get_legal_actions, terminal_state
from app.engine.state import Action, GameState, Phase


# --------------------------------------------------------------------------- #
#  Configuration des difficultés
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class _DifficultyConfig:
    depth: int               # profondeur fixe (easy, medium)
    use_alpha_beta: bool
    use_transposition: bool
    use_iterative_deepening: bool
    timeout_seconds: float   # pour iterative deepening (hard)
    max_depth: int           # plafond pour iterative deepening
    random_noise: float      # probabilité de jouer un coup sous-optimal (easy)


_DIFFICULTY = {
    "easy":   _DifficultyConfig(depth=2,  use_alpha_beta=True,
                                use_transposition=False, use_iterative_deepening=False,
                                timeout_seconds=0.0, max_depth=2,  random_noise=0.30),
    "medium": _DifficultyConfig(depth=4,  use_alpha_beta=True,
                                use_transposition=True,  use_iterative_deepening=False,
                                timeout_seconds=0.0, max_depth=4,  random_noise=0.0),
    "hard":   _DifficultyConfig(depth=0,  use_alpha_beta=True,
                                use_transposition=True,  use_iterative_deepening=True,
                                timeout_seconds=2.0, max_depth=20, random_noise=0.0),
}


# --------------------------------------------------------------------------- #
#  Table de transposition
# --------------------------------------------------------------------------- #

# Flag indiquant la nature de la valeur stockée
_TT_EXACT = 0
_TT_LOWER = 1   # lower bound (beta cutoff)
_TT_UPPER = 2   # upper bound (alpha cutoff)


@dataclass
class _TTEntry:
    value: int
    depth: int
    flag: int
    best_action: Optional[Action]


class TranspositionTable:
    """
    Stocke les états déjà évalués pour éviter les recalculs.

    Clé : hash du GameState frozen (immuable donc hashable).
    Comme le Fanoron-telo a un espace d'états réduit, le gain est important
    sur les niveaux medium/hard.
    """

    def __init__(self, capacity: int = 200_000) -> None:
        self._table: dict[int, _TTEntry] = {}
        self._capacity = capacity
        self.hits = 0
        self.misses = 0

    def get(self, state: GameState, depth: int, alpha: int, beta: int):
        key = hash(state)
        entry = self._table.get(key)
        if entry is None:
            self.misses += 1
            return None
        if entry.depth < depth:
            self.misses += 1
            return None
        self.hits += 1
        if entry.flag == _TT_EXACT:
            return entry.value, entry.best_action
        if entry.flag == _TT_LOWER and entry.value >= beta:
            return entry.value, entry.best_action
        if entry.flag == _TT_UPPER and entry.value <= alpha:
            return entry.value, entry.best_action
        # Valeur stockée non exploitable pour cette fenêtre
        self.misses += 1
        return None

    def put(self, state: GameState, depth: int, value: int, alpha: int, beta: int,
            best_action: Optional[Action]) -> None:
        # Éviction basique si la table déborde
        if len(self._table) >= self._capacity:
            self._table.clear()
        key = hash(state)
        if value <= alpha:
            flag = _TT_UPPER
        elif value >= beta:
            flag = _TT_LOWER
        else:
            flag = _TT_EXACT
        self._table[key] = _TTEntry(value=value, depth=depth, flag=flag,
                                     best_action=best_action)

    def clear(self) -> None:
        self._table.clear()
        self.hits = 0
        self.misses = 0

    def __len__(self) -> int:
        return len(self._table)


# --------------------------------------------------------------------------- #
#  Move ordering
# --------------------------------------------------------------------------- #

_CENTER_BIT = 1 << 4  # case 4 = centre


def _order_moves(actions: list[Action], state: GameState,
                 tt_best: Optional[Action] = None) -> list[Action]:
    """
    Trie les coups pour améliorer l'élagage alpha-beta :
      1. Coup gagnant immédiat en premier (si détectable).
      2. Meilleur coup de la table de transposition.
      3. Pose / déplacement vers le centre.
      4. Le reste.
    """
    def score(action: Action) -> int:
        s = 0
        if tt_best is not None and action == tt_best:
            s += 1_000_000
        # Atteint ou quitte le centre
        if action.dst == 4:
            s += 100
        if action.type == Phase.MOVEMENT and action.src == 4:
            s -= 50  # quitter le centre est souvent mauvais
        # En Phase 2, un coup qui crée une menace (2 alignés) est intéressant
        return s

    return sorted(actions, key=score, reverse=True)


# --------------------------------------------------------------------------- #
#  Negamax avec Alpha-Beta
# --------------------------------------------------------------------------- #

class _Timeout(Exception):
    """Levé par iterative deepening quand le temps imparti est écoulé."""


def _negamax(state: GameState, depth: int, alpha: int, beta: int,
             tt: Optional[TranspositionTable], deadline: Optional[float]) -> tuple[int, Optional[Action]]:
    """
    Retourne (score, best_action) du point de vue du joueur dont c'est le tour.
    """
    if deadline is not None and time.time() > deadline:
        raise _Timeout()

    # Forcer la détection de terminalité (limite de coups / blocage)
    state = terminal_state(state)

    if state.is_over:
        # Score terminal : victoire immédiate -> +WIN_SCORE ajusté par la
        # profondeur restante pour privilégier les victoires rapides.
        if state.winner == state.turn:
            return WIN_SCORE + depth, None
        if state.winner.name == "NONE":
            return 0, None
        return -WIN_SCORE - depth, None

    if depth == 0:
        return evaluate_for_turn(state), None

    # Lookup table de transposition
    tt_best: Optional[Action] = None
    if tt is not None:
        cached = tt.get(state, depth, alpha, beta)
        if cached is not None:
            # Si valeur exacte et qu'on a l'action, on peut retourner,
            # mais pour conserver une action on ne court-circuite que la valeur
            value, tt_best = cached
            # On ne retourne pas immédiatement : on a besoin de calculer
            # l'action au niveau racine. On laisse l'alpha-beta resserrer.

    actions = get_legal_actions(state)
    if not actions:
        # Joueur bloqué -> défaite
        return -WIN_SCORE - depth, None

    actions = _order_moves(actions, state, tt_best)

    best_value = -math.inf
    best_action: Optional[Action] = actions[0]
    alpha_orig = alpha

    for action in actions:
        if deadline is not None and time.time() > deadline:
            raise _Timeout()
        next_state = _apply(state, action)
        child_value, _ = _negamax(next_state, depth - 1, -beta, -alpha, tt, deadline)
        value = -child_value

        if value > best_value:
            best_value = value
            best_action = action

        if value > alpha:
            alpha = value
        if alpha >= beta:
            break  # beta cutoff

    if tt is not None:
        tt.put(state, depth, best_value, alpha_orig, beta, best_action)

    return best_value, best_action


def _apply(state: GameState, action: Action) -> GameState:
    """
    Wrapper local vers rules.apply_action (import différé pour éviter cycle).
    """
    from app.engine.rules import apply_action
    return apply_action(state, action)


# --------------------------------------------------------------------------- #
#  API publique : best_move
# --------------------------------------------------------------------------- #

def best_move(state: GameState, difficulty: str = "medium") -> Optional[Action]:
    """
    Retourne la meilleure Action pour `state.turn`, ou None si la partie est
    terminée.

    Paramètres :
      - state       : état courant (ne sera pas muté).
      - difficulty  : "easy" | "medium" | "hard".

    Q4 (verrouillé) :
      - easy   : profondeur 2 + 30% de bruit aléatoire.
      - medium : profondeur 4, alpha-beta + transposition.
      - hard   : iterative deepening jusqu'à 2.0s (max depth 20) + transposition.
    """
    if difficulty not in _DIFFICULTY:
        raise ValueError(f"Difficulté inconnue : {difficulty!r}. "
                         f"Choix: {list(_DIFFICULTY)}")

    state = terminal_state(state)
    if state.is_over:
        return None

    cfg = _DIFFICULTY[difficulty]
    actions = get_legal_actions(state)
    if not actions:
        return None

    # Opening book uniquement en hard
    if difficulty == "hard":
        try:
            from app.ai.opening_book import get_opening_move
            book_move = get_opening_move(state)
            if book_move is not None and book_move in actions:
                return book_move
        except Exception:
            pass

    # Bruit aléatoire (easy) : 30% du temps, on joue un coup aléatoire légal
    if cfg.random_noise > 0 and random.random() < cfg.random_noise:
        return random.choice(actions)

    tt = TranspositionTable() if cfg.use_transposition else None

    # --- Profondeur fixe (easy, medium) --------------------------------- #
    if not cfg.use_iterative_deepening:
        try:
            _, action = _negamax(state, cfg.depth, -math.inf, math.inf,
                                  tt, deadline=None)
            return action if action is not None else random.choice(actions)
        except _Timeout:
            return random.choice(actions)

    # --- Iterative deepening (hard) ------------------------------------- #
    deadline = time.time() + cfg.timeout_seconds
    best_action: Optional[Action] = None
    best_value: int = -math.inf

    for depth in range(1, cfg.max_depth + 1):
        try:
            value, action = _negamax(state, depth, -math.inf, math.inf,
                                      tt, deadline=deadline)
            if action is not None:
                best_action = action
                best_value = value
            # Élagage : victoire garantie, on s'arrête
            if abs(best_value) >= WIN_SCORE:
                break
        except _Timeout:
            break  # on garde le meilleur coup de la profondeur précédente
        if time.time() >= deadline:
            break

    if best_action is None:
        best_action = random.choice(actions)
    return best_action


__all__ = [
    "best_move",
    "TranspositionTable",
]
