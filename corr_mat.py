import numpy as np
import math
from util import get_loop_density, get_instrument_type

# Implementation of Correlative Matrix approach presented in:
# Jia Lien Hsu, Chih Chin Liu, and Arbee L.P. Chen. Discovering
# nontrivial repeating patterns in music data. IEEE Transactions on
# Multimedia, 3:311–325, 9 2001.
def calc_correlation(melody_seq):
    corr_size = len(melody_seq)
    corr_mat = np.zeros((corr_size, corr_size), dtype='int32')
    corr_dur = np.zeros((corr_size, corr_size), dtype='float')

    for j in range(1, corr_size):
        if melody_seq[0] == melody_seq[j] and melody_seq[0].is_barline():
            corr_mat[0,j] = 1
            corr_dur[0,j] = melody_seq[j].end - melody_seq[0].start
        else:
            corr_mat[0,j] = 0
            corr_dur[0,j] = 0
    for i in range(1, corr_size-1):
        for j in range(i+1, corr_size):
            if melody_seq[i] == melody_seq[j]:
                if corr_mat[i-1, j-1] == 0:
                    if not melody_seq[i].is_barline():
                        continue # loops must start with barlines
                corr_mat[i,j] = corr_mat[i-1, j-1] + 1
                corr_dur[i, j] = corr_dur[i-1, j-1] + melody_seq[j].end - melody_seq[i].start
            else:
                corr_mat[i,j] = 0
                corr_dur[i,j] = 0
    
    return corr_mat, corr_dur


def is_empty_pattern(pattern):
    for note in pattern:
        if len(note.pitches) > 0:
            return False
    return True

def compare_patterns(p1, p2, min_rep_beats): #new pattern, existing pattern
    min_rep_beats = int(round(min_rep_beats))
    if len(p1) < len(p2):
        for i in range(min_rep_beats):
            if p1[i] != p2[i]:
                return 0 #not a substring, theres a mismatch
        return 1 #is a substring
    else:
        for i in range(min_rep_beats):
            if p1[i] != p2[i]:
                return 0 #not a substring, theres a mismatch
        return 2 #existing pattern is substring of the new one, replace it
        
def test_loop_exists(pattern_list, pattern, min_rep_beats):
    for i, pat in enumerate(pattern_list):
        result = compare_patterns(pattern, pat, min_rep_beats)
        if result == 1:
            return -1 #ignore this pattern since its a substring
        if result == 2:
            return i #replace existing pattern with this new longer one
    return None #we're just appending the new pattern

def filter_sub_loops(candidate_indices):
    candidate_indices = dict(sorted(candidate_indices.items()))

    repeats = {}
    final = []
    for duration in candidate_indices.keys():
        curr_start = 0
        curr_end = 0
        curr_dur = 0
        for (start,end,beat) in candidate_indices[duration]:
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

            final.append((start, end, beat, duration))

    return final

# filter based on defined parameters and remove duplicates
def get_valid_loops(track, corr_mat, corr_dur, min_rep_notes=4, min_rep_beats=2.0, min_beats=4.0, max_beats=32.0):
    min_rep_notes += 1 # don't count bar lines as a repetition
    x_num_elem, y_num_elem = np.where(corr_mat == min_rep_notes)

    valid_indices = {}
    for i,x in enumerate(x_num_elem):
        y = y_num_elem[i]
        start_x = x - corr_mat[x,y] + 1
        start_y = y - corr_mat[x,y] + 1
        
        loop_start_time = track.notes[start_x].start
        loop_end_time = track.notes[start_y].start
        beat_sec, loop_beats = track.get_loop_beats(loop_start_time, loop_end_time)
        loop_beats = round(loop_beats,2)
        if loop_beats <= max_beats and loop_beats >= min_beats:
            if loop_beats not in valid_indices:
                valid_indices[loop_beats] = []
            valid_indices[loop_beats].append((x_num_elem[i], y_num_elem[i], beat_sec))
    
    filtered_indices = filter_sub_loops(valid_indices)

    loops = []
    loop_bp = []
    corr_size = corr_mat.shape[0]
    for start_x,start_y,beat_sec,loop_beats in filtered_indices:
        #print(start_x,start_y,beat_sec,loop_beats)
        x = start_x
        y = start_y
        while x+1 < corr_size and y+1 < corr_size and corr_mat[x+1,y+1] > corr_mat[x,y]:
            x = x + 1
            y = y + 1
        beginning = x - corr_mat[x,y] + 1
        duration = corr_dur[x,y] / beat_sec
        end = y - corr_mat[x,y] + 1
        
        if duration >= min_rep_beats and not is_empty_pattern(track.notes[beginning:end]):
            loop = track.notes[beginning:(end+1)]
            #if track.notes[beginning].duration_ticks !=0 or track.notes[end].duration_ticks !=0:
            #    print("SKIPPING, NOT FULL BAR")
            #    continue #loops must be full bar
            loop_density = get_loop_density(loop, loop_beats)
            if loop_density < 0.5:
                # density filter
                continue
            exist_result = test_loop_exists(loops, loop, min_rep_beats)
            start_sec = track.notes[beginning].start
            end_sec = track.notes[end].start
            if exist_result == None:
                loops.append(loop)
                loop_bp.append((start_sec, end_sec, loop_beats, loop_density))
            elif exist_result > 0: #index to replace
                loops[exist_result] = loop
                loop_bp[exist_result] = (start_sec, end_sec, loop_beats, loop_density)

    return loops, loop_bp