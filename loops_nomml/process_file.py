
from __future__ import annotations
from typing import Dict
import numpy as np
from miditok.utils import get_bars_ticks, get_beats_ticks
from miditok.constants import CLASS_OF_INST, INSTRUMENT_CLASSES
from symusic import Score, Track, TimeSignature

from .corr_mat import calc_correlation, get_valid_loops
from .note_set import compute_note_sets


def get_instrument_type(track: Track) -> str:
    if track.is_drum:
        return "Drums"

    return INSTRUMENT_CLASSES[CLASS_OF_INST[0]]["name"]


def create_loop_dict(endpoint_data, track_idx, instrument_type):
    start, end, beats, density = endpoint_data
    return {
        "track_idx": track_idx,
        "instrument_type": instrument_type,
        "start": start,
        "end": end,
        "duration_beats": beats,
        "note_density": density
    }

def detect_loops_from_path(file_info: Dict):
    score = Score(file_info['file_path'][0])
    return detect_loops(score)

def detect_loops(score: Score):
    data = {
        "track_idx": [],
        "instrument_type": [],
        "start": [],
        "end": [],
        "duration_beats": [],
        "note_density": [],
    }
    # Check that there is a time signature. There might be none with abc files
    if len(score.time_signatures) == 0:
        score.time_signatures.append(TimeSignature(0, 4, 4))

    bars_ticks = np.array(get_bars_ticks(score))
    beats_ticks = np.array(get_beats_ticks(score))
    for idx, track in enumerate(score.tracks):
        # cut beats_tick at the end of the track
        if any(track_bars_mask := bars_ticks > track.end()):
            bars_ticks_track = bars_ticks[:np.nonzero(track_bars_mask)[0][0]]
        else:
            bars_ticks_track = bars_ticks

        # cut beats_tick at the end of the track
        if any(track_beats_mask := beats_ticks > track.end()):
            beats_ticks_track = beats_ticks[:np.nonzero(track_beats_mask)[0][0]]
        else:
            beats_ticks_track = beats_ticks

        instrument_type = get_instrument_type(track)
        note_sets = compute_note_sets(track.notes, bars_ticks_track)
        lead_mat = calc_correlation(note_sets)
        _, loop_endpoints = get_valid_loops(note_sets, lead_mat, beats_ticks_track)
        for endpoint in loop_endpoints:
            loop_dict = create_loop_dict(endpoint, idx, instrument_type)
            for key in loop_dict.keys():
                data[key].append(loop_dict[key])

    return data
