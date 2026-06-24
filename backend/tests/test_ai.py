"""
Tests unitaires + tournoi de l'IA Fanoron-telo.

Couvre :
  - Smoke : imports, opening book, legalité des coups retournés.
  - Règles : get_legal_actions, apply_action, victoire immédiate en Phase 1.
  - IA : chaque difficulté renvoie un coup légal ; termine une partie.
  - Tournois : hard >= medium >= easy (sanity check).
  - Performance : temps de réponse < seuil par difficulté.
"""

from __future__ import annotations

import time

import pytest

from app.ai import best_move, evaluate, get_opening_move
from app.ai.evaluation import WIN_SCORE
from app.ai.minimax import TranspositionTable
from app.engine import Action, GameState, Phase, Player, initial_state
from app.engine.rules import (
    apply_action,
    get_legal_actions,
    get_winner,
    is_game_over,
)


# --------------------------------------------------------------------------- #
#  Règles (référence, propriété partagée avec Person A)
# --------------------------------------------------------------------------- #

def test_initial_state_is_empty():
    s = initial_state()
    assert s.phase == Phase.PLACEMENT
    assert s.turn == Player.ONE
    assert s.p1_bb == 0
    assert s.p2_bb == 0
    assert s.p1_to_place == 3
    assert s.p2_to_place == 3
    assert s.move_count == 0
    assert not s.is_over
    assert s.winner == Player.NONE


def test_legal_actions_initial_state():
    s = initial_state()
    actions = get_legal_actions(s)
    assert len(actions) == 9
    for a in actions:
        assert a.type == Phase.PLACEMENT
        assert 0 <= a.dst <= 8
        assert a.src is None


def test_apply_action_alternates_turn():
    s = initial_state()
    a = Action(type=Phase.PLACEMENT, dst=4)
    s2 = apply_action(s, a)
    assert s2.turn == Player.TWO
    assert s2.p1_bb == (1 << 4)
    assert s2.move_count == 1


def test_apply_action_illegal_raises():
    s = initial_state()
    a1 = Action(type=Phase.PLACEMENT, dst=4)
    s = apply_action(s, a1)
    # J1 a joué en 4, J2 rejoue en 4 -> illegal
    a_illegal = Action(type=Phase.PLACEMENT, dst=4)
    with pytest.raises(ValueError):
        apply_action(s, a_illegal)


def test_win_on_placement_phase():
    """Victoire immédiate quand J1 aligne 3 pions pendant la phase de pose."""
    # Cas : J1 a déjà posé 0, 1, et J2 a joué en 4, 8. J1 pose en 2 -> ligne haut
    s = GameState(
        phase=Phase.PLACEMENT,
        turn=Player.ONE,
        p1_bb=(1 << 0) | (1 << 1),
        p2_bb=(1 << 4) | (1 << 8),
        p1_to_place=1,
        p2_to_place=1,
    )
    win_action = Action(type=Phase.PLACEMENT, dst=2)
    s_after = apply_action(s, win_action)
    assert s_after.is_over
    assert s_after.winner == Player.ONE


def test_transition_to_movement_after_6_placements():
    """Quand les 6 pions sont posés sans gagnant, on passe en Phase 2."""
    # J1 a 3 pions, J2 en a 2 -> c'est au tour de J2 (p1_to_place=0, p2_to_place=1)
    s = GameState(
        phase=Phase.PLACEMENT,
        turn=Player.TWO,
        p1_bb=(1 << 0) | (1 << 1) | (1 << 3),
        p2_bb=(1 << 4) | (1 << 7),
        p1_to_place=0,
        p2_to_place=1,
    )
    a = Action(type=Phase.PLACEMENT, dst=8)  # J2 pose son 3e pion en 8
    s_after = apply_action(s, a)
    assert s_after.phase == Phase.MOVEMENT
    assert not s_after.is_over


# --------------------------------------------------------------------------- #
#  Évaluation
# --------------------------------------------------------------------------- #

def test_evaluate_symmetry():
    """evaluate(s, P1) == -evaluate(s, P2) sur état symétrique échangé."""
    s = initial_state()
    # Place 1 pion J1 (symétrie via échange des bitboards)
    s = apply_action(s, Action(type=Phase.PLACEMENT, dst=4))
    score_for_turn = evaluate(s, s.turn)
    # Échange J1 <-> J2 : autre joueur gagne les mêmes avantages
    swapped = GameState(
        phase=s.phase,
        turn=s.turn,
        p1_bb=s.p2_bb,
        p2_bb=s.p1_bb,
        p1_to_place=s.p2_to_place,
        p2_to_place=s.p1_to_place,
    )
    assert score_for_turn == -evaluate(swapped, swapped.turn)


def test_evaluate_terminal_state():
    """Victoire de J1 -> score = +WIN_SCORE du point de vue de J1."""
    s = GameState(
        phase=Phase.MOVEMENT,
        turn=Player.TWO,
        p1_bb=(1 << 0) | (1 << 1) | (1 << 2),
        p2_bb=(1 << 4) | (1 << 8) | (1 << 6),
        p1_to_place=0,
        p2_to_place=0,
        winner=Player.ONE,
        is_over=True,
        move_count=8,
    )
    assert evaluate(s, Player.ONE) == WIN_SCORE
    assert evaluate(s, Player.TWO) == -WIN_SCORE


# --------------------------------------------------------------------------- #
#  Opening book
# --------------------------------------------------------------------------- #

def test_opening_book_first_move_is_center():
    s = initial_state()
    move = get_opening_move(s)
    assert move is not None
    assert move.type == Phase.PLACEMENT
    assert move.dst == 4


def test_opening_book_after_center_taken_returns_corner():
    """Si J1 prend un coin, J2 (opening book) doit répondre par un coin
    diagonalement opposé OU par le centre — pas None."""
    # Cas : J1 pose dans un coin (par exemple 0). Opening book J2 -> coin opposé (8).
    s = initial_state()
    s = apply_action(s, Action(type=Phase.PLACEMENT, dst=0))
    # C'est maintenant au tour de J2
    move = get_opening_move(s)
    assert move is not None
    assert move.type == Phase.PLACEMENT
    # J1 a joué en 0 -> coin ; J2 joue un coin (diagonalement opposé)
    assert move.dst in (8, 4)  # coin opposé (8) ou centre si vide


# --------------------------------------------------------------------------- #
#  IA : chaque difficulté renvoie un coup légal et termine la partie
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("difficulty", ["easy", "medium", "hard"])
def test_best_move_returns_legal_action(difficulty: str):
    s = initial_state()
    action = best_move(s, difficulty)
    assert action is not None
    assert action in get_legal_actions(s)


@pytest.mark.parametrize("difficulty", ["easy", "medium", "hard"])
def test_best_move_terminates(difficulty: str):
    """L'IA doit pouvoir jouer une partie complète contre un random."""
    import random
    rng = random.Random(0)
    s = initial_state()
    nb = 0
    while not is_game_over(s) and nb < 50:
        actions = get_legal_actions(s)
        if not actions:
            break
        if s.turn == Player.ONE:
            a = best_move(s, difficulty)
        else:
            a = rng.choice(actions)
        if a is None:
            break
        s = apply_action(s, a)
        nb += 1
    assert nb > 0
    assert is_game_over(s) or get_winner(s) != Player.NONE or nb >= 50


# --------------------------------------------------------------------------- #
#  Transposition table
# --------------------------------------------------------------------------- #

def test_transposition_table_round_trip():
    s = initial_state()
    a = Action(type=Phase.PLACEMENT, dst=4)
    tt = TranspositionTable()
    tt.put(s, depth=2, value=42, alpha=-999, beta=999, best_action=a)
    result = tt.get(s, depth=2, alpha=-999, beta=999)
    assert result is not None
    value, best = result
    assert value == 42
    assert best == a


def test_transposition_table_deeper_lookup_misses():
    """Une entrée stockée à depth=2 n'est pas fiable pour un lookup à depth=4
    (l'évaluation peut être optimiste)."""
    s = initial_state()
    tt = TranspositionTable()
    # On stocke à depth=2 (peu profond)
    tt.put(s, depth=2, value=10, alpha=-999, beta=999, best_action=None)
    # Lookup à depth=4 doit rejeter (entrée pas assez profonde)
    result = tt.get(s, depth=4, alpha=-999, beta=999)
    assert result is None


# --------------------------------------------------------------------------- #
#  Tournois IA vs IA — hard doit dominer
# --------------------------------------------------------------------------- #

def _play_match(p1_difficulty: str | None, p2_difficulty: str | None,
                max_moves: int = 60, seed: int = 0) -> int:
    """
    Joue une partie J1 vs J2 (None = aléatoire) et renvoie :
      - 1 si J1 gagne
      - 2 si J2 gagne
      - 0 si nul / non terminé
    """
    import random
    rng = random.Random(seed)
    s = initial_state()
    for _ in range(max_moves):
        if is_game_over(s):
            break
        actions = get_legal_actions(s)
        if not actions:
            break
        difficulty = p1_difficulty if s.turn == Player.ONE else p2_difficulty
        if difficulty is None:
            a = rng.choice(actions)
        else:
            a = best_move(s, difficulty)
        if a is None:
            break
        s = apply_action(s, a)
    w = get_winner(s)
    if w == Player.ONE:
        return 1
    if w == Player.TWO:
        return 2
    return 0


def test_hard_beats_easy_most_of_the_time():
    """Hard (J1) vs Easy (J2) sur 10 parties, hard doit gagner plus souvent."""
    wins = 0
    for seed in range(10):
        if _play_match("hard", "easy", seed=seed) == 1:
            wins += 1
    assert wins >= 6, f"Hard n'a gagné que {wins}/10 vs easy"


def test_hard_beats_medium_most_of_the_time():
    """Hard (J1) vs Medium (J2) sur 10 parties."""
    wins = 0
    for seed in range(10):
        if _play_match("hard", "medium", seed=seed) == 1:
            wins += 1
    assert wins >= 6, f"Hard n'a gagné que {wins}/10 vs medium"


def test_medium_beats_easy_most_of_the_time():
    """Medium (J1) vs Easy (J2) sur 10 parties."""
    wins = 0
    for seed in range(10):
        if _play_match("medium", "easy", seed=seed) == 1:
            wins += 1
    assert wins >= 6, f"Medium n'a gagné que {wins}/10 vs easy"


# --------------------------------------------------------------------------- #
#  Performance : temps de réponse max par difficulté
# --------------------------------------------------------------------------- #

def test_medium_responds_quickly():
    s = initial_state()
    s = apply_action(s, Action(type=Phase.PLACEMENT, dst=4))  # centre -> J2
    t0 = time.perf_counter()
    best_move(s, "medium")
    elapsed = time.perf_counter() - t0
    assert elapsed < 0.5, f"Medium trop lent : {elapsed*1000:.0f} ms"


def test_hard_responds_under_timeout():
    s = initial_state()
    s = apply_action(s, Action(type=Phase.PLACEMENT, dst=4))
    t0 = time.perf_counter()
    best_move(s, "hard")
    elapsed = time.perf_counter() - t0
    # Hard a un timeout interne de 2s -> doit répondre en < 2.5s
    assert elapsed < 2.5, f"Hard trop lent : {elapsed*1000:.0f} ms"