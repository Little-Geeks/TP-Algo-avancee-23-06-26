"""
Contrat d'état du jeu Fanoron-telo.

Ce module est la SOURCE DE VÉRITÉ partagée entre :
  - Engine  (rules.py)   : fait évoluer l'état
  - AI     (minimax.py)  : évalue l'état et propose une Action
  - API    (main.py)     : sérialise l'état en JSON pour le frontend

Toute modification ici doit être validée par l'équipe (Phase 0).
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import IntEnum
from typing import Optional


# --------------------------------------------------------------------------- #
#  Énumérations publiques
# --------------------------------------------------------------------------- #

class Phase(IntEnum):
    """Phase courante de la partie."""
    PLACEMENT = 1  # Phase 1 : pose des 6 pions (3 par joueur)
    MOVEMENT = 2   # Phase 2 : déplacement d'un pion vers une case adjacente


class Player(IntEnum):
    """Identifiant d'un joueur. NONE sert pour les cases vides / match nul."""
    NONE = 0
    ONE = 1
    TWO = 2


# --------------------------------------------------------------------------- #
#  Structures de données
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class Action:
    """
    Une action légale dans le jeu.

    - PLACEMENT : seul `dst` est utilisé (`src` doit être None).
    - MOVEMENT  : `src` est la case d'origine, `dst` la case destination.

    L'instance est immuable (frozen) pour pouvoir être réutilisée en sécurité
    et servir de clé dans les tables de transposition si besoin.
    """
    type: Phase              # Phase.PLACEMENT ou Phase.MOVEMENT
    dst: int                 # 0..8 : case cible
    src: Optional[int] = None  # 0..8 : case d'origine (Phase 2 uniquement)

    def __post_init__(self) -> None:
        if not (0 <= self.dst <= 8):
            raise ValueError(f"dst hors plage: {self.dst}")
        if self.src is not None and not (0 <= self.src <= 8):
            raise ValueError(f"src hors plage: {self.src}")
        if self.type == Phase.PLACEMENT and self.src is not None:
            raise ValueError("Une action de PLACEMENT ne doit pas avoir de src")
        if self.type == Phase.MOVEMENT and self.src is None:
            raise ValueError("Une action de MOVEMENT exige un src")


@dataclass(frozen=True)
class GameState:
    """
    État complet et immuable du plateau de Fanoron-telo.

    L'état est `frozen=True` pour :
      - permettre le hashage (clé de table de transposition),
      - garantir qu'aucun module ne mute l'état en place (apply_action renvoie
        un nouvel état, ce qui facilite Undo/Redo via une pile d'états).

    Champs :
      - phase        : 1 = placement, 2 = mouvement
      - turn         : joueur devant jouer (1 ou 2)
      - p1_bb/p2_bb  : bitboards 9 bits des pions de chaque joueur
      - p1_to_place  : nb de pions encore à poser par J1 (Phase 1)
      - p2_to_place  : idem pour J2
      - winner       : Player.ONE / TWO si victoire, NONE si partie en cours
                       ou terminée par nul (cf. is_over).
      - is_over      : True si la partie est terminée (victoire ou blocage).
      - move_count   : nombre total d'actions jouées (debug / limite anti-boucle).
    """
    phase: Phase = Phase.PLACEMENT
    turn: Player = Player.ONE
    p1_bb: int = 0
    p2_bb: int = 0
    p1_to_place: int = 3
    p2_to_place: int = 3
    winner: Player = Player.NONE
    is_over: bool = False
    move_count: int = 0

    # -- Accès pratiques --------------------------------------------------- #

    def player_bb(self, player: Player) -> int:
        """Retourne le bitboard du joueur donné."""
        if player == Player.ONE:
            return self.p1_bb
        if player == Player.TWO:
            return self.p2_bb
        return 0

    def opponent(self) -> Player:
        """Joueur adverse de celui dont c'est le tour."""
        return Player.TWO if self.turn == Player.ONE else Player.ONE

    def to_dict(self) -> dict:
        """
        Sérialisation JSON-friendly pour l'API et le frontend.

        Toutes les valeurs sont des types natifs sérialisables.
        """
        return {
            "phase": int(self.phase),
            "turn": int(self.turn),
            "p1_bb": self.p1_bb,
            "p2_bb": self.p2_bb,
            "p1_positions": _bb_to_list(self.p1_bb),
            "p2_positions": _bb_to_list(self.p2_bb),
            "p1_to_place": self.p1_to_place,
            "p2_to_place": self.p2_to_place,
            "winner": int(self.winner),
            "is_over": self.is_over,
            "move_count": self.move_count,
        }


# --------------------------------------------------------------------------- #
#  Helpers internes
# --------------------------------------------------------------------------- #

def _bb_to_list(bitboard: int) -> list[int]:
    """Convertit un bitboard en liste d'index de cases (0..8)."""
    return [i for i in range(9) if (bitboard >> i) & 1]


# --------------------------------------------------------------------------- #
#  Fabriques d'états initiaux
# --------------------------------------------------------------------------- #

def initial_state() -> GameState:
    """Retourne l'état de départ d'une partie standard."""
    return GameState()


__all__ = [
    "Phase",
    "Player",
    "Action",
    "GameState",
    "initial_state",
]
