# backend/app/engine/board.py

class FanoronaBoard:
    """
    Représentation du plateau de Fanoron-telo utilisant des Bitboards.
    - 0 correspond à une case vide.
    - 1 correspond à la présence d'un pion.
    """

    # --- MASQUES DE VICTOIRE (Alignements de 3) ---
    # Lignes, Colonnes, Diagonales
    # Exemple : Ligne du haut (0, 1, 2) = 2^0 + 2^1 + 2^2 = 1 + 2 + 4 = 7
    WINNING_MASKS = [
        0b000000111,  # Ligne Haut (0, 1, 2) = 7
        0b000111000,  # Ligne Milieu (3, 4, 5) = 56
        0b111000000,  # Ligne Bas (6, 7, 8) = 448
        0b010010010,  # Colonne Gauche (0, 3, 6) = 73
        0b101001001,  # Colonne Milieu (1, 4, 7) = 146
        0b100100100,  # Colonne Droite (2, 5, 8) = 292
        0b100010001,  # Diagonale Principale (0, 4, 8) = 273
        0b001010100   # Diagonale Secondaire (2, 4, 6) = 84
    ]

    # --- MASQUES D'ADJACENCE (Pour les déplacements) ---
    # Définit où un pion peut aller depuis une position donnée.
    # Seules les cases reliées par une ligne sont adjacentes.
    ADJACENT_MASKS = {
        0: 0b000011010,  # Connecté à 1, 3, 4 (2^1 + 2^3 + 2^4) = 26
        1: 0b000010101,  # Connecté à 0, 2, 4 = 21
        2: 0b000110010,  # Connecté à 1, 4, 5 = 50
        3: 0b001010001,  # Connecté à 0, 4, 6 = 81
        4: 0b111111111 ^ 0b000010000, # Connecté à tous les autres (sauf lui-même) = 495
        5: 0b100010100,  # Connecté à 2, 4, 8 = 276
        6: 0b010011000,  # Connecté à 3, 4, 7 = 152
        7: 0b101010000,  # Connecté à 4, 6, 8 = 336
        8: 0b010110000   # Connecté à 4, 5, 7 = 176
    }

    def __init__(self):
        # Initialisation des bitboards pour le Joueur 1 et le Joueur 2 à 0 (vide)
        self.p1_bb = 0b000000000
        self.p2_bb = 0b000000000

    def get_empty_cells(self) -> int:
        """
        Retourne un bitboard représentant toutes les cases vides.
        """
        occupied = self.p1_bb | self.p2_bb
        return (~occupied) & 0b111111111

    def is_winning(self, player_bb: int) -> bool:
        """
        Vérifie si un bitboard contient un alignement gagnant (Phase 1 & 2).
        """
        for mask in self.WINNING_MASKS:
            if (player_bb & mask) == mask:
                return True
        return False

    def can_place(self, position: int) -> bool:
        """
        Vérifie si on peut placer un pion (Phase 1 : Placement).
        """
        bit = 1 << position
        empty_cells = self.get_empty_cells()
        return (empty_cells & bit) > 0

    def get_valid_moves(self, position: int) -> int:
        """
        Retourne un bitboard des destinations valides pour un pion donné (Phase 2 : Mouvement).
        Garantit le déplacement vers une intersection adjacente libre.
        """
        empty_cells = self.get_empty_cells()
        adjacent_cells = self.ADJACENT_MASKS[position]
        
        # Le ET logique bit à bit donne les cases qui sont à la fois adjacentes ET vides
        return adjacent_cells & empty_cells

    def extract_positions(self, bitboard: int) -> list:
        """
        Convertit un bitboard en une liste d'index (0 à 8) pour communiquer avec le Frontend.
        """
        positions = []
        for i in range(9):
            if (bitboard & (1 << i)):
                positions.append(i)
        return positions
