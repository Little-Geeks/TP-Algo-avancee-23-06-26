# backend/app/engine/board.py

class FanoronaBoard:
    """
    Représentation du plateau de Fanoron-telo utilisant des Bitboards.

    Convention de numérotation des cases (position = index de bit, LSB = 0) :

        Plateau visuel :           Index des bits :
            0 --- 1 --- 2              bit 0 | bit 1 | bit 2
            |  \\ |  /  |              -------+-------+-------
            |   \\| /   |              bit 3 | bit 4 | bit 5
            3 --- 4 --- 5              -------+-------+-------
            |   /|\\    |              bit 6 | bit 7 | bit 8
            |  / | \\   |
            6 --- 7 --- 8

    - Un bitboard est un entier 9 bits où le bit i représente la case i.
    - bit = 0 -> case vide, bit = 1 -> pion présent.
    - Exemple : case 0 -> 1<<0 = 1 ; case 8 -> 1<<8 = 256.
    """

    # --- MASQUES DE VICTOIRE (Alignements de 3) ---
    # Lignes, Colonnes, Diagonales. 8 alignements gagnants au total.
    # Chaque masque est la somme des bits des 3 cases composant l'alignement.
    WINNING_MASKS = [
        0b000000111,  # Ligne Haut       (0, 1, 2) = 7
        0b000111000,  # Ligne Milieu     (3, 4, 5) = 56
        0b111000000,  # Ligne Bas        (6, 7, 8) = 448
        0b001001001,  # Colonne Gauche   (0, 3, 6) = 73
        0b010010010,  # Colonne Milieu   (1, 4, 7) = 146
        0b100100100,  # Colonne Droite   (2, 5, 8) = 292
        0b100010001,  # Diagonale \\     (0, 4, 8) = 273
        0b001010100,  # Diagonale /      (2, 4, 6) = 84
    ]

    # --- MASQUES D'ADJACENCE (Pour les déplacements de la Phase 2) ---
    # Pour chaque case i, donne le bitboard des cases reliées par une ligne.
    # Topologie : les diagonales ne passent que par le centre (case 4).
    #   -> Les coins (0, 2, 6, 8) ont 3 voisins ; les bords (1, 3, 5, 7) ont 3 voisins ;
    #      le centre (4) a 8 voisins.
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
