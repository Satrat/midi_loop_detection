import pretty_midi
from corr_mat import *
from track import Track
from util import create_loop_dict
import os

def run_file(data):
    file_path = data["file_path"][0]
    file_name = data["file_name"][0]
    data["file"] = []
    data["track_number"] = []
    data["instrument_type"] = []
    data["time_signature"] = []
    data["start"] = []
    data["end"] = []
    data["beats"] = []
    data["density"] = []

    if not os.path.exists(file_path):
        print(f"File {file_path} does not exist, skipping")
        return data
    try:
        pm = pretty_midi.PrettyMIDI(file_path)
    except:
        print(f"MIDI file {file_path} could not be parsed, skipping")
        return data

    for idx, instrument in enumerate(pm.instruments):
        instrument_type = get_instrument_type(instrument)
        track = Track(pm, instrument)
        note_list = track.notes
        lead_mat, lead_dur = calc_correlation(note_list)
        _, loop_endpoints = get_valid_loops(track, lead_mat, lead_dur)
        for endpoint in loop_endpoints:
            time_sig = track.get_time_sig_at_time(endpoint[0])
            if time_sig is None:
                continue
            loop_dict = create_loop_dict(endpoint, idx, instrument_type, time_sig, file_name)
            for key in loop_dict.keys():
                data[key].append(loop_dict[key])

    return data