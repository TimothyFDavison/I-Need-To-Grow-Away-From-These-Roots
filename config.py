import numpy as np


# Generate or use pre-saved files
use_existing_files = False
generate_intermediate_files = False
chords_file = "chorasdfds.txt"
graph_file = "chords_graph.pkl"
log_to_file = False

# Audio settings
sample_rate = 44100
duration = 8
t = np.linspace(0, duration, int(sample_rate * duration), False)
fade = True
attack_time = duration * .2  # fade in
release_time = duration * .2  # fade out

# Base chord settings
A4_freq = 440.0
lower_octave = 3
upper_octave = 4

# Supplemental note settings
lower_length_supplemental = .04
upper_length_supplemental = .8
lower_octave_supplemental = -2
upper_octave_supplemental = 3
repetition_length_threshold = .1
lower_repetition_bound = 2
upper_repetition_bound = 4
scaling_factor = .3
pause_lower_bound = 1
pause_upper_bound = duration / 2

# Chords to use
notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
intervals = {
    "major": [0, 4, 7],  # major third, perfect fifth
    "minor": [0, 3, 7],  # minor third, perfect fifth
    "major_seventh": [0, 4, 7, 11],  # major third, perfect fifth, major seventh
    "minor_seventh": [0, 3, 7, 10],  # minor third, perfect fifth, minor seventh
    # "dominant_seventh": [0, 4, 7, 10],  # major third, perfect fifth, minor seventh
    # "diminished": [0, 3, 6],  # minor third, diminished fifth
    # "augmented": [0, 4, 8],  # major third, augmented fifth
}
