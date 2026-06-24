# backend/app/engine/rules.py

from app.engine.board import FanoronaBoard

class FanoronaGame:
    """
    Gestionnaire des règles et des états du jeu Fanoron-telo.
    Assure la cohérence des phases, l'alternance des joueurs et la détection de victoire.
    """

    def __init__(self):
        self.board = FanoronaBoard()
        self.current_player = 1  # 1 pour Joueur 1 (P1), 2 pour Joueur 2 (P2)
        self.phase = 1           # 1 = Phase de Placement, 2 = Phase de Mouvement
        self.pieces_placed = 0   # Compteur total de pions posés (maximum 6)
        self.game_over = False
        self.winner = None       # None, 1 ou 2

    def play_turn(self, action_type: str, from_position: int = None, to_position: int = None) -> bool:
        """
        Point d'entrée unique de l'API pour jouer un coup.
        - action_type: 'place' ou 'move'
        - from_position: requis pour 'move'
        - to_position: requis pour 'place' et 'move'
        Retourne True si l'action a été validée et exécutée, False sinon.
        """
        if self.game_over:
            return False

        if self.phase == 1 and action_type == 'place' and to_position is not None:
            return self._handle_placement(to_position)
            
        elif self.phase == 2 and action_type == 'move' and from_position is not None and to_position is not None:
            return self._handle_movement(from_position, to_position)
            
        return False

    def _handle_placement(self, position: int) -> bool:
        """
        Gère la Phase 1 : Placement alterné des pions.
        """
        # 1. Vérifier si la case est libre via le Bitboard
        if not self.board.can_place(position):
            return False

        # 2. Placer le pion en modifiant le Bitboard du joueur actuel
        move_bit = 1 << position
        if self.current_player == 1:
            self.board.p1_bb |= move_bit
            current_bb = self.board.p1_bb
        else:
            self.board.p2_bb |= move_bit
            current_bb = self.board.p2_bb

        self.pieces_placed += 1

        # 3. Vérification immédiate de victoire (alignement pendant la phase 1)
        if self.board.is_winning(current_bb):
            self.game_over = True
            self.winner = self.current_player
            return True

        # 4. Transition automatique vers la Phase 2 lorsque 6 pions sont posés
        if self.pieces_placed == 6:
            self.phase = 2

        # 5. Changement de tour
        self._switch_player()
        return True

    def _handle_movement(self, from_pos: int, to_pos: int) -> bool:
        """
        Gère la Phase 2 : Déplacement des pions vers une intersection adjacente libre.
        """
        from_bit = 1 << from_pos
        to_bit = 1 << to_pos
        
        # 1. Vérifier si le pion de départ appartient bien au joueur actuel
        current_bb = self.board.p1_bb if self.current_player == 1 else self.board.p2_bb
        if not (current_bb & from_bit):
            return False

        # 2. Obtenir les mouvements valides (adjacents et vides) depuis ce Bitboard
        valid_moves = self.board.get_valid_moves(from_pos)
        if not (valid_moves & to_bit):
            return False  # La destination n'est pas adjacente ou est occupée

        # 3. Appliquer le déplacement sur le Bitboard (Retrait + Ajout)
        if self.current_player == 1:
            self.board.p1_bb &= ~from_bit  # Extinction du bit de départ
            self.board.p1_bb |= to_bit     # Allumage du bit d'arrivée
            current_bb = self.board.p1_bb
        else:
            self.board.p2_bb &= ~from_bit
            self.board.p2_bb |= to_bit
            current_bb = self.board.p2_bb

        # 4. Vérification de victoire (alignement après déplacement)
        if self.board.is_winning(current_bb):
            self.game_over = True
            self.winner = self.current_player
            return True

        # 5. Changement de tour
        self._switch_player()
        return True

    def _switch_player(self):
        """Alterne le tour entre le Joueur 1 et le Joueur 2."""
        self.current_player = 2 if self.current_player == 1 else 1

    def get_game_state(self) -> dict:
        """
        Exporte l'état actuel du jeu.
        Idéal pour formater la réponse JSON de votre API FastAPI.
        """
        return {
            "p1_positions": self.board.extract_positions(self.board.p1_bb),
            "p2_positions": self.board.extract_positions(self.board.p2_bb),
            "current_player": self.current_player,
            "phase": self.phase,
            "pieces_placed": self.pieces_placed,
            "game_over": self.game_over,
            "winner": self.winner
        }
