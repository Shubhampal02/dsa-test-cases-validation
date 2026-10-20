import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import calculate_expected_outputs as calc


def test_search_rotated_array_found():
    assert calc.search_rotated_array([4, 5, 6, 7, 0, 1, 2], 0) == 4


def test_search_rotated_array_missing():
    assert calc.search_rotated_array([4, 5, 6, 7, 0, 1, 2], 3) == -1


def test_game_of_life():
    board = [
        [0, 1, 0],
        [0, 0, 1],
        [1, 1, 1],
        [0, 0, 0],
    ]
    expected = [
        [0, 0, 0],
        [1, 0, 1],
        [0, 1, 1],
        [0, 1, 0],
    ]
    assert calc.game_of_life(board) == expected


def test_game_of_life_does_not_modify_input():
    board = [[1, 1], [1, 0]]
    original = [row[:] for row in board]
    calc.game_of_life(board)
    assert board == original
