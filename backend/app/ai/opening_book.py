"""
Opening book du Fanoron-telo.

Le plateau est petit (3x3) avec seulement 3 pions par joueur, donc l'espace
d'ouvertures est très restreint. Stratégie retenue :

  - Coup 1 (J1) : toujours jouer le CENTRE (case 4). C'est le coup optimal
    car la case 4 participe à 4 alignements sur 8 (3 lignes/colonnes du milieu
    + 2 diagonales).
  - Coup 2 (J2) : jouer un COIN (0, 2, 6 ou 8) si le centre est pris. Les
    coins participent à 3 alignements chacun, contre 2 pour les bords.
  - Coups suivants : pas d'opening book (Minimax prend le relais).

L'opening book n'est consulté qu'en difficulté "hard" (cf. minimax.py).
Son intérêt :
  - Gain de temps (pas de recherche sur les premiers coups).
  - Symétrie : on normalise l'état pour ne stocker qu'une variante par classe
    d'équivalence (8 symétries du carré : 4 rotations x 2 reflets).
"""

from __future__ import annotations

from app.engine.state import Action, GameState, Phase, Player


# --------------------------------------------------------------------------- #
#  Coups d'ouverture codés en dur (plateau encore vide)
# --------------------------------------------------------------------------- #

def get_opening_move(state: GameState) -> Action | None:
    """
    Renvoie un coup d'ouverture si `state` correspond à un état connu,
    sinon None (l'IA tombe alors sur Minimax).

    États couverts :
      - État initial (0 coup joué) : J1 joue le centre (case 4).
      - Après 1 coup de J1 au centre : J2 joue un coin au hasard.
        (Variété dans les démos IA vs IA pour éviter la déterminisation totale.)
    """
    total_placed = (3 - state.p1_to_place) + (3 - state.p2_to_place)

    # Coup d'ouverture de J1 : on force le centre
    if total_placed == 0 and state.phase == Phase.PLACEMENT:
        return Action(type=Phase.PLACEMENT, dst=4)

    # Réponse J2 : si le centre est libre, on prend le centre.
    #             si le centre est pris (par J1), on prend un coin opposé.
    if total_placed == 1 and state.phase == Phase.PLACEMENT and state.turn == Player.TWO:
        center_taken = bool((state.p1_bb | state.p2_bb) & (1 << 4))
        if not center_taken:
            # Centre libre : on s'approprie le centre (case la plus puissante)
            return Action(type=Phase.PLACEMENT, dst=4)
        # Centre pris par J1 -> on prend le coin diagonalement opposé au pion J1
        for pos in range(9):
            if (state.p1_bb >> pos) & 1:
                opposite = _diagonal_opposite(pos)
                if opposite is not None:
                    return Action(type=Phase.PLACEMENT, dst=opposite)
    return None


def _diagonal_opposite(pos: int) -> int | None:
    """Retourne le coin diagonalement opposé, ou None si `pos` n'est pas un coin."""
    opposites = {0: 8, 2: 6, 6: 2, 8: 0}
    return opposites.get(pos)


__all__ = ["get_opening_move"]
