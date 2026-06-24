"""
Fonction d'évaluation statique du Fanoron-telo.

Convention (Q5 du contrat - verrouillée) :
  - Victoire du `player` : +WIN_SCORE, avec bonus de profondeur pour privilégier
    les victoires rapides (géré dans minimax.py, pas ici).
  - Défaite du `player` : -WIN_SCORE.
  - Sinon : score heuristique > 0 si `player` est avantagé, < 0 sinon.

L'évaluation est symétrique : evaluate(s, J1) == -evaluate(s, J2) pour tout
état non terminal, ce qui permet d'utiliser le Negamax.

Heuristiques utilisées :
  1. Menaces d'alignement à 2 pions ouverts (avec case vide pour compléter).
  2. Contrôle du centre (case 4) — clé car le centre participe à 4 alignements.
  3. Mobilité (nombre de coups légaux en Phase 2).
  4. Pièces placées (Phase 1) — déjà alignables.
"""

from __future__ import annotations

from app.engine.board import FanoronaBoard
from app.engine.state import GameState, Phase, Player


# Score maximal (en valeur absolue) hors victoire.
# Une victoire vaut ±WIN_SCORE (cf. minimax.py pour le bonus de profondeur).
WIN_SCORE: int = 1_000_000

# Poids heuristiques (réglables — calibrés empiriquement pour Fanoron-telo)
W_TWO_OPEN: int = 50      # 2 pions alignés + 3e case libre (menace directe)
W_TWO_BLOCKED: int = 10   # 2 pions alignés mais 3e case bloquée
W_CENTER: int = 30        # contrôle du centre (case 4)
W_MOBILITY: int = 2       # par coup légal d'avance en Phase 2
W_PIECE_PLACED: int = 5   # par pion posé en Phase 1


def _popcount(x: int) -> int:
    return bin(x).count("1")


def _count_open_threats(player_bb: int, opponent_bb: int) -> tuple[int, int]:
    """
    Compte les menaces d'alignement pour `player_bb`.
    Retourne (open_threats, blocked_threats) où :
      - open_threats = alignements avec 2 pions du joueur et la 3e case VIDE
        (le joueur peut gagner au prochain coup)
      - blocked_threats = alignements avec 2 pions du joueur et la 3e case
        occupée par l'adversaire (menace neutralisée)
    """
    open_t = blocked_t = 0
    for mask in FanoronaBoard.WINNING_MASKS:
        n_player = _popcount(player_bb & mask)
        if n_player != 2:
            continue
        # La 3e case du masque : est-elle vide ou adversaire ?
        third_bit = mask & ~player_bb  # bit de la case non occupée par le joueur
        if third_bit & opponent_bb:
            blocked_t += 1
        elif not (third_bit & (player_bb | opponent_bb)):
            open_t += 1
    return open_t, blocked_t


def evaluate(state: GameState, player: Player) -> int:
    """
    Score statique du `state` du point de vue de `player`.

    Symétrique : evaluate(s, A) == -evaluate(s, B) pour les états non terminaux.
    """
    # --- États terminaux : score garanti à ±WIN_SCORE --------------------- #
    if state.is_over:
        if state.winner == player:
            return WIN_SCORE
        if state.winner == Player.NONE:
            return 0
        return -WIN_SCORE

    my_bb = state.player_bb(player)
    opp_bb = state.p1_bb if player == Player.TWO else state.p2_bb
    my_open, my_blocked = _count_open_threats(my_bb, opp_bb)
    opp_open, opp_blocked = _count_open_threats(opp_bb, my_bb)

    score = 0
    score += W_TWO_OPEN * (my_open - opp_open)
    score += W_TWO_BLOCKED * (my_blocked - opp_blocked)

    # Contrôle du centre (case 4) — participe à 4 alignements (lignes, milieu, diagonales)
    center_bit = 1 << 4
    if my_bb & center_bit:
        score += W_CENTER
    elif opp_bb & center_bit:
        score -= W_CENTER

    # Pièces placées (Phase 1) : incite à occuper le plateau
    if state.phase == Phase.PLACEMENT:
        score += W_PIECE_PLACED * (_popcount(my_bb) - _popcount(opp_bb))

    # Mobilité (Phase 2 uniquement — en Phase 1 la "mobilité" = cases vides,
    # donc peu discriminante)
    if state.phase == Phase.MOVEMENT:
        # Approche légère : on compte les voisins vides de mes pions
        my_mobility = 0
        opp_mobility = 0
        empty = ~(state.p1_bb | state.p2_bb) & 0b111111111
        for pos in range(9):
            if (my_bb >> pos) & 1:
                my_mobility += _popcount(
                    FanoronaBoard.ADJACENT_MASKS[pos] & empty
                )
            elif (opp_bb >> pos) & 1:
                opp_mobility += _popcount(
                    FanoronaBoard.ADJACENT_MASKS[pos] & empty
                )
        score += W_MOBILITY * (my_mobility - opp_mobility)

    return score


def evaluate_for_turn(state: GameState) -> int:
    """
    Score du point de vue du joueur dont c'est le tour.
    Pratique pour Negamax : on évalue toujours "pour le joueur qui joue".
    """
    return evaluate(state, state.turn)


__all__ = [
    "WIN_SCORE",
    "evaluate",
    "evaluate_for_turn",
]
