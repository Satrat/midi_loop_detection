# MIDI Loop Detection

This repository contains the dataset processing code for the paper 
"The GigaMIDI Dataset with Loops and Expressive Music Performance Detection."

## Repository Layout

[**/GigaMIDI**](./GigaMIDI): Code for creating the full GigaMIDI dataset from
source files, and README with example code for loading and processing the 
data set using the `datasets` library

[**/loops_nomml**](./loops_nomml): Source files for loop detection algorithm 
and expressive performance detection algorithm

[**/scripts**](./scripts): Scripts and code notebooks for analyzing the 
GigaMIDI dataset and the loop dataset

[**/tests**](./tests): E2E tests for expressive performance detection and 
loop extractions

## Running Loop Detection

Included with GigaMIDI dataset is a collection of all loops identified in the 
dataset between 4 and 32 bars in length, with a minimum density of 0.5 notes 
per beat. For our purposes, we consider a segment of a track to be loopable if 
it is bookended by a repeated phrase of a minimum length (at least 2 beats 
and 4 note events)

![Loop example](./loops_nomml/loop_ex_labeled.png)

### Starter Code

To run loop detection on a single MIDI file, use the `detect_loops` function
```python
from loops_nomml import detect_loops
from symusic import Score

score = Score("tests\midi_files\Mr. Blue Sky.mid")
loops = detect_loops(score)
print(loops)
```

The output will contain all the metadata needed to locate the loop within the 
file. Start and end times are represented as MIDI ticks, and density is 
given in units of notes per beat:
```
{'track_idx': [0, 0, 0, 0, 1, 1, 2, 2, 2, 3, 3, 3, 3, 3, 4, 5], 'instrument_type': ['Piano', 'Piano', 'Piano', 'Piano', 'Piano', 'Piano', 'Piano', 'Piano', 'Piano', 'Drums', 'Drums', 'Drums', 'Drums', 'Drums', 'Piano', 'Piano'], 'start': [238080, 67200, 165120, 172800, 1920, 97920, 15360, 216960, 276480, 7680, 195840, 122880, 284160, 117120, 49920, 65280], 'end': [241920, 82560, 180480, 188160, 3840, 99840, 17280, 220800, 291840, 9600, 211200, 138240, 291840, 130560, 51840, 80640], 'duration_beats': [8.0, 32.0, 32.0, 32.0, 4.0, 4.0, 4.0, 8.0, 32.0, 4.0, 32.0, 32.0, 16.0, 28.0, 4.0, 32.0], 'note_density': [0.75, 1.84375, 0.8125, 0.8125, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.8125, 2.46875, 2.4375, 2.5, 0.5, 0.6875]}  
```

### Batch Processing Loops

We also provide a script, `main.py` that batch extracts all loops in a 
dataset. This requires that you have downloaded GigaMIDI, see the [dataset README](./GigaMIDI/README.md) for instructions on doing this. Once you have the dataset downloaded, update the `DATA_PATH` and `METADATA_NAME` globals to reflect the location of GigaMIDI on your machine and run the script:

```python
python main.py
```