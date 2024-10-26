from itertools import combinations
import random
import time

import networkx as nx
import numpy as np
import pickle
import simpleaudio as sa

import config


def load_chords():
    """
    Load chords from a file, if pre-saved.
    """
    try:
        chords = [
            x.split() for x in open(config.chords_file, 'r').readlines()
        ]
    except Exception as e:
        print(f"Could not open chords file: {e}")
        print("Proceeding with auto-generation of chords")
        return get_chords()
    return chords


def load_graph(chords, frequencies):
    """
    Load chords if you have them
    """
    try:
        with open(config.graph_file, 'rb') as f:
            G = pickle.load(f)
    except Exception as e:
        print(f"Could not open graph file: {e}")
        print("Proceeding with auto-generation of graph")
        return generate_graph(chords, frequencies)
    return G


def get_inversions(chord):
    """
    Yield inversion combinations from a set of input notes. Octave jumps are indicated by "+"

    Input: [C E G]
    Output: [[C E G], [E+ G C], [G+ C+ E]]
    """
    inversions = []
    for i in range(len(chord)):
        inversion = chord[i:] + chord[:i]
        inversion = [n + '+' if j < i else n for j, n in enumerate(inversion)]
        inversions.append(inversion)
    return inversions


def get_chords(save_chords=config.generate_intermediate_files):
    """

    :return:
    """
    # Generate a set of chords, organized by root
    root_chords = {}
    for root in config.notes:
        for chord_type, interval_pattern in config.intervals.items():
            chord_name = f"{root} {chord_type.replace('_', ' ')}"
            chord = [(config.notes[(config.notes.index(root) + interval) % 12]) for interval in interval_pattern]
            inversions = get_inversions(chord)
            root_chords[chord_name] = inversions

    # Expand the list of chords to cover specific octaves
    all_chords = []
    for chord_name, inversions in root_chords.items():
        for i, chord in enumerate(inversions):
            for octave in range(config.lower_octave, config.upper_octave):
                new_entry = []
                for note in chord:
                    if "+" in note:
                        new_entry.append(note[:-1] + f"{octave + 1}")
                    else:
                        new_entry.append(note + f"{octave}")
                all_chords.append(new_entry)

    # Optionally save the chords to a file for reuse
    if save_chords:
        try:
            with open(config.chords_file, "w") as f:
                for chord in all_chords:
                    f.write(" ".join(chord))
                    f.write("\n")
        except Exception as e:
            print(f"Could not save chords file: {e}")
            print("Skipping...")
            return get_chords()
    return all_chords


def generate_frequencies():
    """
    Produce frequency mappings for each chord.
    """
    note_frequencies = {}
    for octave in range(2, 6):  # C0 to B8
        for i, note in enumerate(config.notes):
            # Calculate the number of semitones from A4
            n = (octave - 4) * 12 + (i - 9)  # i=9 corresponds to A in each octave
            frequency = config.A4_freq * (2 ** (n / 12))
            note_name = f"{note}{octave}"
            note_frequencies[note_name] = round(frequency, 2)
    return note_frequencies


def generate_graph(chords, note_frequencies, save_graph=config.generate_intermediate_files):
    """
    Produce a NetworkX graph in which nodes are chords, and edges are assigned to any two chords which share all but
    one note.
    """
    # Create chord graph
    G = nx.Graph()

    # Generate chord labels
    i = 0
    for chord in chords:
        G.add_node(
            f"chord_{i}",
            notes=chord,
            frequencies=[note_frequencies[x] for x in chord]
        )
        i += 1

    # Add edges based on the shared note criteria
    for chord1, chord2 in combinations(G.nodes(), 2):
        chord1_data = G.nodes[chord1]
        chord2_data = G.nodes[chord2]
        chord1_roots = [x[:-1] for x in chord1_data["notes"]]
        chord2_roots = [x[:-1] for x in chord2_data["notes"]]
        non_intersection = set(chord1_roots) ^ set(chord2_roots)
        if len(non_intersection) == 1:
            G.add_edge(chord1, chord2)

    if save_graph:
        try:
            with open(config.graph_file, 'wb') as f:
                pickle.dump(G, f)
        except Exception as e:
            print(f"Could not save graphs file: {e}")
            print("Skipping...")
            return get_chords()
    return G


def generate_chord_wave(frequencies, fade=config.fade, t=config.t, scaling_factor=1.0):
    """
    Generate a waveform as a numpy array for a given set of frequencies..
    """
    # Generate sine waves for each frequency in the chord
    waves = [0.5 * np.sin(2 * np.pi * freq * t) for freq in frequencies]
    chord_wave = sum(waves)

    # Fade in and out effect
    if fade:
        envelope = np.ones_like(t)
        attack_samples = min(int(config.attack_time * config.sample_rate), len(t) // 2)
        release_samples = min(int(config.release_time * config.sample_rate), len(t) // 2)
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        envelope[-release_samples:] = np.linspace(1, 0, release_samples)
        chord_wave = chord_wave * envelope  # apply fade

    # Normalize to 16-bit range
    chord_wave = (chord_wave * scaling_factor * (2**15 - 1) / np.max(np.abs(chord_wave))).astype(np.int16)
    return chord_wave


def play_base_chord(G, node):
    """

    """
    inv = generate_chord_wave(G.nodes[node]["frequencies"])
    play_obj = sa.play_buffer(inv, 1, 2, 44100)
    play_obj.wait_done()


def play_supplement(G, current_node, duration=config.duration):
    """

    """
    start_time = time.time()
    while time.time() - start_time < duration:

        # Create a waveform envelope, set repetition depending on waveform length
        ttl = random.uniform(config.lower_length_supplemental, config.upper_length_supplemental)
        repetition = 1 if ttl > config.repetition_length_threshold else random.randint(
            config.lower_repetition_bound, config.upper_repetition_bound
        )
        ttl = np.linspace(0, ttl, int(config.sample_rate * ttl), False)

        # Generate the note
        octave = random.randrange(config.lower_octave_supplemental, config.upper_octave_supplemental)
        note = random.choice(G.nodes[current_node]["frequencies"]) * (2 ** octave)
        note = generate_chord_wave([note], t=ttl, fade=True, scaling_factor=config.scaling_factor)

        # Repeat waveform according to repetition threshold
        for i in range(repetition):
            play_obj = sa.play_buffer(note, 1, 2, config.sample_rate)
            play_obj.wait_done()

        # Pause for a random amount of time
        wait_time = random.uniform(config.pause_lower_bound, config.pause_upper_bound)
        time.sleep(wait_time)
