# Author: Donato Quartuccia
# Last Modified: 2022-12-06

import heapq
import itertools
from collections.abc import Iterable


# ------------------------------------- Day One -------------------------------------
def day_one(file: str, num_elves: int) -> tuple[int, int]:
    """Return maximum calories among all elves and sum of top-n elves"""
    top_calories = [0] * num_elves
    maximum_calories = current_calories = 0
    with open(file) as calorie_data:
        for line in calorie_data:
            try:
                current_calories += int(line)
            except ValueError:
                current_calories = 0
            maximum_calories = max(maximum_calories, current_calories)
            if current_calories > top_calories[0]:
                heapq.heapreplace(top_calories, current_calories)
    return maximum_calories, sum(top_calories)


# ------------------------------------- Day Two -------------------------------------
def decode_as_moves(file: str) -> tuple[tuple[str, str]]:
    """Decode input such that X -> A, Y -> B and Z -> C assuming space-delimited input"""
    decoder = dict(zip("XYZ", "ABC"))
    with open(file) as move_data:
        decoded_moves = (
            tuple(decoder.get(m, m) for m in move.strip().split(' '))
            for move in move_data
        )
        return tuple(decoded_moves)


def decode_as_outcomes(file: str) -> tuple[tuple[str, str]]:
    """Decode input such that X -> loss, Y -> tie and Z -> win assuming space-delimited input"""
    xyz_to_index = {value: index for index, value in enumerate("XYZ")}
    corresponding_move = {
        'A': ('C', 'A', 'B'),
        'B': ('A', 'B', 'C'),
        'C': ('B', 'C', 'A'),
    }
    with open(file, 'r') as move_data:
        moves = (move.strip().split(' ') for move in move_data)
        pairs = ((first, xyz_to_index[second]) for first, second in moves)
        decoded_moves = ((move, corresponding_move[move][index]) for move, index in pairs)
        return tuple(decoded_moves)


def day_two(moves: Iterable[tuple[str, str]]) -> tuple[int, int]:
    """Return the total number of points from rock-paper-scissor move pairs, for first and
    second player respectively. Input is A for 'rock', B for 'paper', C for 'scissors'
    """
    base_points = {'A': 1, 'B': 2, 'C': 3}

    win, tie, lose = 6, 3, 0
    wins = ('A', 'C'), ('C', 'B'), ('B', 'A')
    ties = ('A', 'A'), ('B', 'B'), ('C', 'C')
    losses = (tuple(reversed(move)) for move in wins)

    point_values = itertools.chain(
        itertools.zip_longest(wins, (), fillvalue=win),
        itertools.zip_longest(ties, (), fillvalue=tie),
        itertools.zip_longest(losses, (), fillvalue=lose),
    )
    victory = dict(point_values)

    player_one_points = sum(base_points[first] + victory[first, second] for first, second in moves)
    player_two_points = sum(base_points[second] + victory[second, first] for first, second in moves)
    return player_one_points, player_two_points


# ------------------------------------ Day Three ------------------------------------
def day_three():
    pass


if __name__ == "__main__":
    max_calories, max_three_calories = day_one("input/day_1.txt", 3)
    print(f"Day 1: {max_calories}, {max_three_calories}")

    score_as_moves = day_two(decode_as_moves("input/day_2.txt"))
    score_as_targets = day_two(decode_as_outcomes("input/day_2.txt"))
    print(f"Day 2: {score_as_moves[1]}, {score_as_targets[1]}")
