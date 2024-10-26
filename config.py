import numpy as np


# Generate or use pre-saved files
use_existing_files = False
generate_intermediate_files = False  # will save chords list, network graph as files
chords_file = "chords.txt"
graph_file = "chords_graph.pkl"

# Audio settings
sample_rate = 44100
duration = 8  # seconds that the base chord will play
t = np.linspace(0, duration, int(sample_rate * duration), False)
fade = True
attack_time = duration * .1  # fade in (s)
release_time = duration * .1  # fade out

# Base chord settings
A4_freq = 440.0
lower_octave = 3  # lower/upper bounds for base chord octave
upper_octave = 4

# Supplemental note settings
lower_length_supplemental = .04  # lower/upper bounds for individual note duration
upper_length_supplemental = 1.5
lower_octave_supplemental = -2  # lower/upper bounds for individual note octavt
upper_octave_supplemental = 3
repetition_length_threshold = .4  # duration threshold below which individual note will repeat
lower_repetition_bound = 3  # lower/upper bounds for individual note repetition
upper_repetition_bound = 6
scaling_factor = .3  # amplitude scaling factor to control relative loudness of individual note to base chord
pause_lower_bound = 1  # lower/upper bounds for pause time after individual note
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
