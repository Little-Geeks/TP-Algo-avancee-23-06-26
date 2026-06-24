"""
Moteur de règles du Fanoron-telo.

Implémentation de référence par la personne B (Lead IA) pour débloquer
le développement et les tests de l'IA. La personne A (Lead Engine) peut
reprendre, optimiser ou remplacer ce fichier tant que les SIGNATURES
publiques documentées dans docs/CONTRAT.md sont respectées.

Règles (rappel du sujet) :
  - Phase 1 (Placement) : 3 pions par joueur, pose alternée sur case libre.
                          Victoire immédiate dès qu'un joueur aligne ses 3 pions.
  - Phase 2 (Mouvement) après les 6 poses : déplacement d'un pion vers une
                          case ADJACENTE LIBRE. Victoire dès l'alignement.
"""

from __future__ import annotations

from app.engine.board import FanoronaBoard
from app.engine.state import Action, GameState, Phase, Player


# --------------------------------------------------------------------------- #
#  Génération des actions légales
# --------------------------------------------------------------------------- #

def get_legal_actions(state: GameState) -> list[Action]:
    """Toutes les actions légales pour le joueur dont c'est le tour."""
    if state.is_over:
        return []

    occupied = state.p1_bb | state.p2_bb
    empty_mask = (~occupied) & 0b111111111

    if state.phase == Phase.PLACEMENT:
        return [
            Action(type=Phase.PLACEMENT, dst=i)
            for i in range(9)
            if (empty_mask >> i) & 1
        ]

    # Phase 2 : déplacement d'un pion du joueur courant vers une case
    # adjacente libre.
    my_bb = state.player_bb(state.turn)
    actions: list[Action] = []
    for src in range(9):
        if not ((my_bb >> src) & 1):
            continue
        reachable = FanoronaBoard.ADJACENT_MASKS[src] & empty_mask
        for dst in range(9):
            if (reachable >> dst) & 1:
                actions.append(Action(type=Phase.MOVEMENT, src=src, dst=dst))
    return actions


def is_valid_action(state: GameState, action: Action) -> bool:
    """True si l'action est légale dans l'état donné (sans lever d'exception)."""
    try:
        return action in get_legal_actions(state)
    except ValueError:
        return False


# --------------------------------------------------------------------------- #
#  Transition d'état (immuable)
# --------------------------------------------------------------------------- #

def apply_action(state: GameState, action: Action) -> GameState:
    """
    Applique `action` à `state` et retourne un NOUVEL état.
    Lève ValueError si l'action est illégale.
    """
    if state.is_over:
        raise ValueError("La partie est terminée")

    legal = get_legal_actions(state)
    if action not in legal:
        raise ValueError(f"Action illégale : {action}")

    player = state.turn
    opponent = state.opponent()

    if player == Player.ONE:
        new_p1, new_p2 = state.p1_bb, state.p2_bb
        p1_to_place, p2_to_place = state.p1_to_place, state.p2_to_place
        if action.type == Phase.PLACEMENT:
            new_p1 |= (1 << action.dst)
            p1_to_place -= 1
        else:
            new_p1 &= ~(1 << action.src)
            new_p1 |= (1 << action.dst)
        next_p1_bb, next_p2_bb = new_p1, new_p2
    else:  # Player.TWO
        new_p1, new_p2 = state.p1_bb, state.p2_bb
        p1_to_place, p2_to_place = state.p1_to_place, state.p2_to_place
        if action.type == Phase.PLACEMENT:
            new_p2 |= (1 << action.dst)
            p2_to_place -= 1
        else:
            new_p2 &= ~(1 << action.src)
            new_p2 |= (1 << action.dst)
        next_p1_bb, next_p2_bb = new_p1, new_p2

    # Détection de victoire sur le bitboard du joueur qui vient de jouer
    player_bb_after = next_p1_bb if player == Player.ONE else next_p2_bb
    has_won = FanoronaBoard.is_winning(FanoronaBoard(), player_bb_after)

    if has_won:
        return GameState(
            phase=state.phase,
            turn=opponent,
            p1_bb=next_p1_bb,
            p2_bb=next_p2_bb,
            p1_to_place=p1_to_place,
            p2_to_place=p2_to_place,
            winner=player,
            is_over=True,
            move_count=state.move_count + 1,
        )

    # Transition Phase 1 -> Phase 2 une fois les 6 pions posés
    if state.phase == Phase.PLACEMENT and p1_to_place == 0 and p2_to_place == 0:
        next_phase = Phase.MOVEMENT
    else:
        next_phase = state.phase

    return GameState(
        phase=next_phase,
        turn=opponent,
        p1_bb=next_p1_bb,
        p2_bb=next_p2_bb,
        p1_to_place=p1_to_place,
        p2_to_place=p2_to_place,
        winner=Player.NONE,
        is_over=False,
        move_count=state.move_count + 1,
    )


# --------------------------------------------------------------------------- #
#  État terminal
# --------------------------------------------------------------------------- #

# Au-delà de ce nombre de coups en Phase 2 sans gagnant, on déclare match nul
# (Q2 du contrat - option simple choisie : move_count > 50).
_DRAW_MOVE_LIMIT = 50


def is_game_over(state: GameState) -> bool:
    """True si la partie est terminée."""
    if state.is_over:
        return True
    if state.phase == Phase.MOVEMENT and state.move_count >= _DRAW_MOVE_LIMIT:
        return True
    if not get_legal_actions(state):
        return True
    return False


def get_winner(state: GameState) -> Player:
    """Player.ONE / TWO si victoire, Player.NONE si nul ou en cours."""
    if state.winner != Player.NONE:
        return state.winner
    if state.phase == Phase.MOVEMENT and state.move_count >= _DRAW_MOVE_LIMIT:
        return Player.NONE
    # Blocage : plus aucun coup légal -> le joueur dont c'est le tour perd
    # (variant du Fanoron-telo : on ne peut pas passer son tour).
    if state.is_over or not get_legal_actions(state):
        return state.opponent()
    return Player.NONE


def is_draw(state: GameState) -> bool:
    """True si la partie est terminée sans gagnant."""
    return is_game_over(state) and get_winner(state) == Player.NONE


def terminal_state(state: GameState) -> GameState:
    """
    Retourne l'état "finalisé" (is_over + winner mis à jour) si la partie
    vient de se terminer par blocage ou limite de coups.
    Utile pour l'IA qui doit savoir qu'un état non marqué is_over est terminal.
    """
    if state.is_over:
        return state
    if state.phase == Phase.MOVEMENT and state.move_count >= _DRAW_MOVE_LIMIT:
        return GameState(
            phase=state.phase,
            turn=state.turn,
            p1_bb=state.p1_bb,
            p2_bb=state.p2_bb,
            p1_to_place=state.p1_to_place,
            p2_to_place=state.p2_to_place,
            winner=Player.NONE,
            is_over=True,
            move_count=state.move_count,
        )
    if not get_legal_actions(state):
        # Le joueur dont c'est le tour est bloqué -> il perd
        winner = state.opponent()
        return GameState(
            phase=state.phase,
            turn=state.turn,
            p1_bb=state.p1_bb,
            p2_bb=state.p2_bb,
            p1_to_place=state.p1_to_place,
            p2_to_place=state.p2_to_place,
            winner=winner,
            is_over=True,
            move_count=state.move_count,
        )
    return state


__all__ = [
    "get_legal_actions",
    "is_valid_action",
    "apply_action",
    "is_game_over",
    "get_winner",
    "is_draw",
    "terminal_state",
]
