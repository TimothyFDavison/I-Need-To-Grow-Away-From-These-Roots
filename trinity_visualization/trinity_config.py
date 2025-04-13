# Generate or use pre-saved files
trinity_graph = "trinity_graph.json"

# Distance metric variables
discrete_octave_steps = True  # when True, induces clear separation of octaves within network
octave_separation_coefficient = 6  # scales distance induced by octave differences between chords
note_separation_coefficient = .2  # scales distance induced by note differences between chords

# Color to chord associations in nodes
circle_of_fifths = ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'Db', 'Ab', 'Eb', 'Bb', 'F']
root_hues = {root: (i / len(circle_of_fifths)) for i, root in enumerate(circle_of_fifths)}
color_lightness = .7
color_saturation = .5
