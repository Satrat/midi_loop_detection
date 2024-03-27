class NoteSet:
    def __init__(self, pm, start, end):
        self.start = start
        self.end = end
        self.start_tick = pm.time_to_tick(start)
        self.end_tick = pm.time_to_tick(end)
        self.duration = self.end - self.start
        self.duration_ticks = self.end_tick - self.start_tick
        self.pitches = set()

    def add_note(self, note):
        self.pitches.add(note.pitch)

    def fits_in_set(self, start_tick, end_tick):
        if start_tick != self.start_tick:
            return False
        if (end_tick - start_tick) != self.duration_ticks:
            return False
        return True
    
    def is_barline(self):
        return self.start_tick == self.end_tick and len(self.pitches) == 0
    
    def __str__(self):
        return f"NoteSet({self.start}, {self.duration}, {self.pitches})"
    
    def __eq__(self, other):
        if self.duration_ticks != other.duration_ticks:
            return False
        
        if len(self.pitches) != len(other.pitches):
            return False
        for m in self.pitches:
            if m not in other.pitches:
                return False
        
        return True
    
    def __lt__(self, other):
        return self.start_tick < other.start_tick