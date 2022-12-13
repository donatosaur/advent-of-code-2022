# Author: Donato Quartuccia
# Last Modified: 2022-12-12
import heapq
import itertools
import string
import re
from collections import deque
from collections.abc import Iterable, Iterator
from data_structures import DirectoryStack


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


def day_four(file: str) -> tuple[int, int]:
    """Return the number of overlapping interval pairs by line

    Assumes interval pairs are comma-delimited and interval bounds within those are dash-delimited
    """
    with open(file) as interval_data:
        intervals = (line.strip().split(',') for line in interval_data)
        pairwise_intervals = [parse_intervals(*pair) for pair in intervals]

    contained = sum(is_contained(*pair) for pair in pairwise_intervals)
    overlapping = sum(is_overlapping(*pair) for pair in pairwise_intervals)
    return contained, overlapping


# ------------------------------------ Day Five -------------------------------------
def sorted_values_by_key(d: dict):
    return (value for _, value in sorted(d.items(), key=lambda item: item[0]))


def day_five(file: str) -> tuple[str, str]:
    """Parse 1-indexed columnar crate diagram. Assumes all instructions are valid and every fourth
    char from index 1 in the diagram represents a crate identifier (or is blank), as follows::
             [J] [T]     [H]
            # ^1  ^5  ^9  ^13
            ⋮
            <blank line>
            move <num_boxes> from <source> to <destination>
            ⋮

    Return the top of each 1-indexed stack of crates after all move instructions are executed,
    in order from lowest to highest indexed stack, both assuming one box is moved at a time and
    assuming boxes are moved in batches
    """
    stacks = {}
    with open(file) as crate_data:
        while line := crate_data.readline().strip('\n'):
            enumerated_crates = (
                (i // 4 + 1, char)  # 1-indexed
                for i, char in enumerate(line)
                if (i - 1) % 4 == 0 and char.isalpha()
            )
            for index, crate in enumerated_crates:
                stacks.setdefault(index, []).append(crate)
        for stack in stacks.values():
            stack.reverse()

        pattern = re.compile(r"\b(\d+)\b")  # num_boxes, source, destination
        matches = (pattern.findall(line) for line in crate_data)
        instructions = [match for match in matches if len(match) == 3]

    single_move = stacks
    multi_move = {index: stack[:] for index, stack in stacks.items()}
    for instruction in instructions:
        num_boxes, source, destination = (int(digit) for digit in instruction)
        single_move[destination].extend(
            single_move[source].pop() for _ in range(num_boxes)
        )
        multi_move[destination].extend(
            reversed([multi_move[source].pop() for _ in range(num_boxes)])
        )

    single_move_top_crates = ''.join(stack[-1] for stack in sorted_values_by_key(single_move))
    multi_move_top_crates = ''.join(stack[-1] for stack in sorted_values_by_key(multi_move))
    return single_move_top_crates, multi_move_top_crates


# ------------------------------------- Day Six -------------------------------------
def first_unique_window(sequence: Iterable, window_size: int) -> int:
    """Return the index of the first position in the sequence such that a window of size
    ``window_size`` is full of unique elements, or -1 if there is no such position"""
    buffer = deque(maxlen=window_size)
    for index, char in enumerate(sequence):
        if len(set(buffer)) == window_size:
            return index
        buffer.append(char)
    return -1


def day_six(file: str) -> tuple[int, int]:
    """Return the index of the start of signal marker for windows of size 4 and 14"""
    with open(file) as signal_data:
        signal = signal_data.read()
    return first_unique_window(signal, 4), first_unique_window(signal, 14)


# ------------------------------------ Day Seven ------------------------------------
def parse_prompt(prompt_line: str) -> tuple[str, str]:
    """Return the command and its first argument (if any) from a space-delimited prompt"""
    _, command, *args = prompt_line.split(maxsplit=2)
    return command, args[0] if args else ''


def parse_cli_log(log: Iterable[str], prompt: str = '$') -> Iterator[tuple[str, ...]]:
    """Return an iterator over tuples of parsed commands, their args, and their output (if any)"""
    with_output = ()
    log = (line.rstrip() for line in log)
    for is_command, lines in itertools.groupby(log, key=lambda s: s.startswith(prompt)):
        if is_command:
            # the following group is the last command's output (if any); yield with output instead
            *without_output, with_output = (parse_prompt(prompt_line) for prompt_line in lines)
            yield from without_output
        else:
            yield tuple(itertools.chain(with_output, lines))


def parse_ls(output: Iterable[str]) -> int:
    """Return the child directories and sum of all files among the output of the ls command"""
    parsed_output = (line.split(' ', maxsplit=1) for line in output)
    return sum(int(prefix) for prefix, _ in parsed_output if prefix.isdigit())


def day_seven(file: str) -> tuple[int, int]:
    """Return the total size of all directories not exceeding size 100,000 and the size of the
    smallest directory to be deleted such that 30,000,000 units of size are available"""
    total_disk_space, required_disk_space = 70_000_000, 30_000_000
    directory_stack = DirectoryStack(max_tracked_directory_size=100_000)
    directory_sizes = {}
    with open(file) as log:
        for command, arg, *output in parse_cli_log(log):
            match command, arg:
                case "cd", ".":
                    pass
                case "cd", "..":
                    path, size = directory_stack.pop()
                    directory_sizes[path] = size
                case "cd", _:
                    directory_stack.push(arg, 0)
                case "ls", _:
                    size = parse_ls(output)
                    directory_stack.update_size(size)
                case _:
                    raise ValueError(f"Command {command} not supported")
    while directory_stack:
        path, size = directory_stack.pop()
        directory_sizes[path] = size
    free_space = total_disk_space - directory_sizes['/']
    if (size_to_free := required_disk_space - free_space) <= 0:
        return directory_stack.accumulator, 0

    directory_sizes = (size for size in directory_sizes.values() if size >= size_to_free)
    size_to_delete = min(directory_sizes, default=0)
    return directory_stack.accumulator, size_to_delete


# ------------------------------------ Day Eight ------------------------------------
def day_eight():
    pass


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

    top_crates_single_move, top_crates_multi_move = day_five("input/day_5.txt")
    print(f"Day 5: {top_crates_single_move}, {top_crates_multi_move}")

    size_4, size_14 = day_six("input/day_6.txt")
    print(f"Day 6: {size_4}, {size_14}")

    size_all_directories, size_to_be_deleted = day_seven("input/day_7.txt")
    print(f"Day 7: {size_all_directories}, {size_to_be_deleted}")
