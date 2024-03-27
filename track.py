from note_set import NoteSet

class Track:
    def __init__(self, p_midi, instrument):
        tempo_times, tempo_vals = p_midi.get_tempo_changes()
        self.tempo_changes = list(zip(tempo_times, tempo_vals))
        self.downbeats = [NoteSet(p_midi, start=db, end=db) for db in p_midi.get_downbeats()]
        self.p_midi = p_midi
        
        note_list = instrument.notes
        processed_notes = []
        for note in note_list:
            note_start_tick = p_midi.time_to_tick(note.start)
            note_end_tick = p_midi.time_to_tick(note.end)
            
            start_new_set = len(processed_notes) == 0 or not processed_notes[-1].fits_in_set(note_start_tick, note_end_tick)
            if start_new_set:
                processed_notes.append(NoteSet(p_midi, start=note.start, end=note.end))
            processed_notes[-1].add_note(note)

        self.notes = processed_notes + self.downbeats #TODO: combine this with downbeats in a list
        self.notes.sort()
        
    def get_tempo_at_time(self, curr_time_wall):
        if len(self.tempo_changes) == 1:
            return self.tempo_changes[0][1]
        for idx in range(len(self.tempo_changes)):
            tempo_start = self.tempo_changes[idx][0]
            tempo = self.tempo_changes[idx][1]
            if idx == len(self.tempo_changes) - 1:
                return tempo
            tempo_end = self.tempo_changes[idx + 1][0]
            if curr_time_wall >= tempo_start and curr_time_wall < tempo_end:
                return tempo 
            
    def get_loop_beats(self, start_time, end_time):
        tempo = self.get_tempo_at_time(start_time)
        beat_sec = (60. / tempo)

        return beat_sec, (end_time - start_time) / beat_sec
    