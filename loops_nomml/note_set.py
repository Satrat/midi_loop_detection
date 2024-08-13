
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

    from symusic import Note
    from symusic.core import NoteTickList


def compute_note_sets(notes: NoteTickList, beats_ticks: Sequence[int]) -> list[NoteSet]:
    # a NoteSet is a set of pitches that occur at the same start and end times
    processed_notes = []
    for note in notes:
        start_new_set = len(processed_notes) == 0 or not processed_notes[-1].fits_in_set(note.start, note.end)
        if start_new_set:
            processed_notes.append(NoteSet(start=note.start, end=note.end))
        processed_notes[-1].add_note(note)

    notes = processed_notes + [NoteSet(start=db, end=db) for db in beats_ticks]
    notes.sort()
    return notes


class NoteSet:
    def __init__(self, start: int, end: int) -> None:
        self.start = start
        self.end = end
        self.duration = self.end - self.start
        self.pitches = set()

    def add_note(self, note: Note) -> None:
        self.pitches.add(note.pitch)

    def fits_in_set(self, start: int, end: int) -> bool:
        return start == self.start and end == self.end

    def is_barline(self) -> bool:
        return self.start == self.end and len(self.pitches) == 0

    def __str__(self) -> str:
        return f"NoteSet({self.start}, {self.duration}, {self.pitches})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, NoteSet):
            return False

        if self.duration != other.duration:
            return False
        if len(self.pitches) != len(other.pitches):
            return False

        for m in self.pitches:
            if m not in other.pitches:
                return False

        return True

    def __lt__(self, other: object):
        return self.start < other.start
