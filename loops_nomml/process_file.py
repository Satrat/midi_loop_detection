
from __future__ import annotations

import numpy as np
from miditok.utils import get_beats_ticks
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


"""def get_time_sig_or_tempo_at_tick(list_: TempoTickList | TimeSignatureTickList, tick: int) -> TimeSignature | Tempo:
    if len(list_) == 0:
        return TimeSignature(0, 4, 4) if isinstance(list_, TimeSignatureTickList) else Tempo(0, 120)

    idx = 0
    for i, ts_or_tempo in enumerate(list_):
        if ts_or_tempo.time > tick:
            break
        idx = i

    return list_[idx]"""  # TODO remove this, unused?


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

    beats_ticks = np.array(get_beats_ticks(score))
    for idx, track in enumerate(score.tracks):
        # cut beats_tick at the end of the track
        if any(track_beats_mask := beats_ticks > track.end()):
            beats_ticks_track = beats_ticks[:np.nonzero(track_beats_mask)[0][0]]
        else:
            beats_ticks_track = beats_ticks
        instrument_type = get_instrument_type(track)
        note_sets = compute_note_sets(track.notes, beats_ticks_track)
        lead_mat = calc_correlation(note_sets)
        _, loop_endpoints = get_valid_loops(note_sets, lead_mat, beats_ticks_track)
        for endpoint in loop_endpoints:
            loop_dict = create_loop_dict(endpoint, idx, instrument_type)
            for key in loop_dict.keys():
                data[key].append(loop_dict[key])

    return data
