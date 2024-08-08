
from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from .note_set import NoteSet

if TYPE_CHECKING:
    from collections.abc import Sequence

    from symusic import Note


# Implementation of Correlative Matrix approach presented in:
# Jia Lien Hsu, Chih Chin Liu, and Arbee L.P. Chen. Discovering
# nontrivial repeating patterns in music data. IEEE Transactions on
# Multimedia, 3:311–325, 9 2001.
def calc_correlation(note_sets: Sequence[NoteSet]):
    corr_size = len(note_sets)
    corr_mat = np.zeros((corr_size, corr_size), dtype='int16')

    # Complete the first row
    for j in range(1, corr_size):
        if note_sets[0] == note_sets[j] and note_sets[0].is_barline():
            corr_mat[0, j] = 1
    # Complete rest of the correlation matrix
    for i in range(1, corr_size - 1):
        for j in range(i + 1, corr_size):
            if note_sets[i] == note_sets[j]:
                if corr_mat[i - 1, j - 1] == 0:
                    if not note_sets[i].is_barline():
                        continue  # loops must start with barlines TODO but these are actually downbeats?
                corr_mat[i, j] = corr_mat[i - 1, j - 1] + 1

    return corr_mat


def get_loop_density(loop: Sequence[NoteSet], num_beats: int | float) -> float:
    return len([n_set for n_set in loop if n_set.start != n_set.end]) / num_beats


def is_empty_pattern(pattern: Sequence[Note]) -> bool:
    for note in pattern:
        if len(note.pitches) > 0:
            return False
    return True


def compare_patterns(p1, p2, min_rep_beats):  #new pattern, existing pattern
    min_rep_beats = int(round(min_rep_beats))
    if len(p1) < len(p2):
        for i in range(min_rep_beats):
            if p1[i] != p2[i]:
                return 0  #not a substring, theres a mismatch
        return 1  #is a substring
    else:
        for i in range(min_rep_beats):
            if p1[i] != p2[i]:
                return 0  #not a substring, theres a mismatch
        return 2  #existing pattern is substring of the new one, replace it


def test_loop_exists(pattern_list, pattern, min_rep_beats):
    for i, pat in enumerate(pattern_list):
        result = compare_patterns(pattern, pat, min_rep_beats)
        if result == 1:
            return -1  #ignore this pattern since its a substring
        if result == 2:
            return i  #replace existing pattern with this new longer one
    return None  #we're just appending the new pattern


def filter_sub_loops(candidate_indices):
    candidate_indices = dict(sorted(candidate_indices.items()))

    repeats = {}
    final = []
    for duration in candidate_indices.keys():
        curr_start = 0
        curr_end = 0
        curr_dur = 0
        for start, end in candidate_indices[duration]:
            if start in repeats and repeats[start][0] == end:
                continue

            if start == curr_end:
                curr_end = end
                curr_dur += duration
            else:
                if curr_start != curr_end:
                    repeats[curr_start] = (curr_end, curr_dur)
                curr_start = start
                curr_end = end
                curr_dur = duration

            final.append((start, end, duration))

    return final


def get_duration_beats(start: int, end: int, ticks_beats: Sequence[int]) -> float:
    idx_beat_previous = None
    idx_beat_first_in = None
    idx_beat_last_in = None
    idx_beat_after = None

    for bi, beat_tick in enumerate(ticks_beats):
        if idx_beat_first_in is None and beat_tick >= start:
            idx_beat_first_in = bi
            idx_beat_previous = max(bi - 1, 0)
        elif idx_beat_last_in is None and beat_tick == end:
            idx_beat_last_in = idx_beat_after = bi
        elif idx_beat_last_in is None and beat_tick > end:
            idx_beat_last_in = max(bi - 1, 0)
            idx_beat_after = bi
    if idx_beat_after is None:
        idx_beat_after = idx_beat_last_in + ticks_beats[-1] - ticks_beats[-2]  # TODO what if length 0?

    beat_length_before = ticks_beats[idx_beat_first_in] - ticks_beats[idx_beat_previous]
    if beat_length_before > 0:
        num_beats_before = (ticks_beats[idx_beat_first_in] - ticks_beats[idx_beat_previous]) / beat_length_before
    else:
        num_beats_before = 0
    beat_length_after = ticks_beats[idx_beat_after] - ticks_beats[idx_beat_last_in]
    if beat_length_after > 0:
        num_beats_after = (ticks_beats[idx_beat_after] - ticks_beats[end]) / beat_length_after
    else:
        num_beats_after = 0
    return float(idx_beat_last_in - idx_beat_first_in + num_beats_before + num_beats_after)


# filter based on defined parameters and remove duplicates
def get_valid_loops(
    note_sets,
    corr_mat,
    ticks_beats,
    min_rep_notes=4,
    min_rep_beats=2.0,
    min_beats=4.0,
    max_beats=32.0,
    min_loop_note_density: float = 0.5,
):
    min_rep_notes += 1  # don't count bar lines as a repetition
    x_num_elem, y_num_elem = np.where(corr_mat == min_rep_notes)

    # Parse the correlation matrix to retrieve the loops starts/ends ticks
    # keys are loops durations in beats, values tuples of indices TODO ??
    valid_indices = {}
    for i, x in enumerate(x_num_elem):
        y = y_num_elem[i]
        start_x = x - corr_mat[x, y] + 1
        start_y = y - corr_mat[x, y] + 1

        loop_start_time = note_sets[start_x].start
        loop_end_time = note_sets[start_y].start
        loop_num_beats = round(get_duration_beats(loop_start_time, loop_end_time, ticks_beats), 2)
        if max_beats >= loop_num_beats >= min_beats:
            if loop_num_beats not in valid_indices:
                valid_indices[loop_num_beats] = []
            valid_indices[loop_num_beats].append((x_num_elem[i], y_num_elem[i]))

    filtered_indices = filter_sub_loops(valid_indices)

    loops = []
    loop_bp = []
    corr_size = corr_mat.shape[0]
    for start_x, start_y, loop_num_beats in filtered_indices:
        x = start_x
        y = start_y
        while x + 1 < corr_size and y + 1 < corr_size and corr_mat[x + 1, y + 1] > corr_mat[x, y]:
            x = x + 1
            y = y + 1
        beginning = x - corr_mat[x, y] + 1
        end = y - corr_mat[x, y] + 1
        start_tick = note_sets[beginning].start
        end_tick = note_sets[end].start
        duration_beats = get_duration_beats(start_tick, end_tick, ticks_beats)

        if duration_beats >= min_rep_beats and not is_empty_pattern(note_sets[beginning:end]):
            loop = note_sets[beginning:(end + 1)]
            # if track.notes[beginning].duration_ticks !=0 or track.notes[end].duration_ticks !=0:
            #    print("SKIPPING, NOT FULL BAR")
            #    continue #loops must be full bar
            loop_density = get_loop_density(loop, loop_num_beats)
            if loop_density < min_loop_note_density:
                continue
            exist_result = test_loop_exists(loops, loop, min_rep_beats)
            if exist_result is None:
                loops.append(loop)
                loop_bp.append((start_tick, end_tick, loop_num_beats, loop_density))
            elif exist_result > 0:  # index to replace
                loops[exist_result] = loop
                loop_bp[exist_result] = (start_tick, end_tick, loop_num_beats, loop_density)

    return loops, loop_bp
