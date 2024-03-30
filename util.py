
def get_loop_density(loop, num_beats):
    num_onsets = 0
    for note_set in loop:
        if note_set.start != note_set.end:
            num_onsets += 1
    return float(num_onsets) / num_beats

def create_loop_dict(endpoint_data, track_idx, instrument_type, time_sig, file_path):
    start, end, beats, density = endpoint_data
    return {
        "file": file_path,
        "track_number": track_idx,
        "instrument_type": instrument_type,
        "time_signature": str(time_sig[0]) + "/" + str(time_sig[1]),
        "start": start,
        "end": end,
        "beats": beats,
        "density": density
    }

def get_instrument_type(pm_instrument):
    if pm_instrument.is_drum:
        return "DRUM"
    
    midi_program = pm_instrument.program + 1
    if midi_program <= 8:
        return "PIANO"
    elif midi_program <= 16:
        return "CHROMATIC_PERCUSSION"
    elif midi_program <= 24:
        return "ORGAN"
    elif midi_program <= 32:
        return "GUITAR"
    elif midi_program <= 40:
        return "BASS"
    elif midi_program <= 48:
        return "STRINGS"
    elif midi_program <= 56:
        return "ENSEMBLE"
    elif midi_program <= 64:
        return "BRASS"
    elif midi_program <= 72:
        return "REED"
    elif midi_program <= 80:
        return "PIPE"
    elif midi_program <= 88:
        return "SYNTH_LEAD"
    elif midi_program <= 96:
        return "SYNTH_PAD"
    elif midi_program <= 104:
        return "SYNTH_EFFECT"
    elif midi_program <= 112:
        return "ETHNIC"
    elif midi_program <= 120:
        return "PERCUSSIVE"
    else:
        return "SOUND_EFFECT"
    