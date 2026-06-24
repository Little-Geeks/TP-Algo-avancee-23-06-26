"""Package IA du Fanoron-telo.

Import public :
    from app.ai import best_move, evaluate, get_opening_move, TranspositionTable
"""

from app.ai.evaluation import WIN_SCORE, evaluate, evaluate_for_turn
from app.ai.minimax import TranspositionTable, best_move
from app.ai.opening_book import get_opening_move

__all__ = [
    "WIN_SCORE",
    "evaluate",
    "evaluate_for_turn",
    "best_move",
    "get_opening_move",
    "TranspositionTable",
]
