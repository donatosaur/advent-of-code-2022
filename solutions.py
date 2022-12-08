# Author: Donato Quartuccia
# Last Modified: 2022-12-06

import heapq
import itertools
import string
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
    with open(file) as move_data:
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
def intersect_all(*args: Iterable) -> set:
    """Return the intersection of all passed iterables"""
    first, *rest = args
    return set(first).intersection(*rest)


def day_three(file: str) -> tuple[int, int]:
    """Return the total priority of all items common to compartments of each elf's rucksack
    and the total priority of the common item between each group of elves

    Assumes are two compartments per line, evenly partitioned around the midpoint and elves
    are grouped into triplets
    """
    values = {char: index for index, char in enumerate(string.ascii_letters, start=1)}
    with open(file) as rucksack_data:
        rucksacks = [rucksack.strip() for rucksack in rucksack_data]

    midpoints = (len(rucksack) // 2 for rucksack in rucksacks)
    common_items_by_compartment = itertools.chain.from_iterable(
        set(rucksack[:midpoint]) & set(rucksack[midpoint:])
        for rucksack, midpoint in zip(rucksacks, midpoints)
    )

    tripled_rucksack_iterator = [iter(rucksacks)] * 3
    grouped_rucksacks = zip(*tripled_rucksack_iterator)
    common_items_by_group = itertools.chain.from_iterable(
        intersect_all(*group)
        for group in grouped_rucksacks
    )

    compartment_value = sum(values[item] for item in common_items_by_compartment)
    thirds_values = sum(values[item] for item in common_items_by_group)

    return compartment_value, thirds_values


# ------------------------------------ Day Four -------------------------------------
def is_contained(interval_one: tuple[int, int], interval_two: tuple[int, int]) -> bool:
    """Return True if one interval is contained by the other"""
    left_one, right_one = interval_one
    left_two, right_two = interval_two
    one_contains_two = left_one <= left_two and right_one >= right_two
    two_contains_one = left_one >= left_two and right_one <= right_two
    return one_contains_two or two_contains_one


def is_overlapping(interval_one: tuple[int, int], interval_two: tuple[int, int]) -> bool:
    """Return True if one interval partially or completely overlaps the other"""
    first, second = sorted((interval_one, interval_two))
    return first[1] >= second[0]


def parse_intervals(*interval_strings: str) -> tuple[tuple[int, ...], ...]:
    """Return a tuple of boundaries from `start-end` dash-delimited interval strings"""
    intervals = (tuple(int(boundary) for boundary in s.split('-')) for s in interval_strings)
    return tuple(intervals)


def day_four(file: str):
    """Return the number of overlapping interval pairs by line

    Assumes interval pairs are comma-delimited and interval bounds within those are dash-delimited
    """
    with open(file) as interval_data:
        intervals = (line.strip().split(',') for line in interval_data)
        pairwise_intervals = [parse_intervals(*pair) for pair in intervals]

    contained = sum(is_contained(*pair) for pair in pairwise_intervals)
    overlapping = sum(is_overlapping(*pair) for pair in pairwise_intervals)

    return contained, overlapping


if __name__ == "__main__":
    max_calories, max_three_calories = day_one("input/day_1.txt", 3)
    print(f"Day 1: {max_calories}, {max_three_calories}")

    score_as_moves = day_two(decode_as_moves("input/day_2.txt"))
    score_as_targets = day_two(decode_as_outcomes("input/day_2.txt"))
    print(f"Day 2: {score_as_moves[1]}, {score_as_targets[1]}")

    by_rucksack, by_group = day_three("input/day_3.txt")
    print(f"Day 3: {by_rucksack}, {by_group}")

    fully_overlapping, partially_overlapping = day_four("input/day_4.txt")
    print(f"Day 4: {fully_overlapping}, {partially_overlapping}")
