import colorsys
from itertools import combinations
import json
import logging

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from sklearn.manifold import MDS

import trinity_config


# Set up logging infrastructure
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def chord_color_mapping(chord):
    """
    Generate a mapping from chord names (e.g. C major seventh) to colors (e.g. #FFFFFFFF)
    """
    # Retrieve chord from input
    root, chord_type = chord.split(" ", 1)
    hue = trinity_config.root_hues.get(root, 0)

    # Convert HSL to hex color
    r, g, b = colorsys.hls_to_rgb(hue, trinity_config.color_lightness, trinity_config.color_saturation)
    color_hex = f"#{int( r *255):02x}{int( g *255):02x}{int( b *255):02x}"
    return color_hex


def distance_metric(chord1, chord2):
    """
    Input: chordN = [A3 C3 E3] ...

    Define a distance metric using the following ruleset:
        - Add 1 if the chord2 is an inversion of chord1
        - Add 1 for each difference in the average (mode) octave of the chord
        - Add 2 for each difference in root note of the chord
    """
    # Return 0 if all notes are the same
    if chord1 == chord2:
        return 0

    # Define metric
    distance = 0

    # Octave distance
    if trinity_config.discrete_octave_steps:
        octave1 = max(set([x[-1] for x in chord1]), key=[x[-1] for x in chord1].count)
        octave2 = max(set([x[-1] for x in chord2]), key=[x[-1] for x in chord2].count)
        distance += abs(int(octave1) - int(octave2)) * trinity_config.octave_separation_coefficient
    else:
        octave1 = [float(x[-1]) for x in chord1]
        octave1 = sum(octave1)/len(octave1)
        octave2 = [float(x[-1]) for x in chord2]
        octave2 = sum(octave2)/len(octave2)
        distance += abs(int(octave1) - int(octave2)) * trinity_config.octave_separation_coefficient

    # Root note distance
    non_intersection = len(set([x[:-1] for x in chord1]) ^ set([x[:-1] for x in chord2]))
    distance += 1 + non_intersection * trinity_config.note_separation_coefficient
    return distance


def generate_vector_space(chords):
    """
    Takes in a list of chords. Uses the distance_metric function to produce pairwise distances between
    each chord, then uses multidimensional scaling to convert pairwise distances into a 3D vector space
    """
    # Log progress
    logger.info("Generating a 3D vector space from input chords...")

    # Retrieve pairwise distances
    enumerated_chords = [chord for sublist in list(chords.values()) for chord in sublist]
    distance_matrix = np.zeros((len(enumerated_chords), len(enumerated_chords)))
    for i in range(len(enumerated_chords)):
        for j in range(len(enumerated_chords)):
            chord1 = enumerated_chords[i]
            chord2 = enumerated_chords[j]
            distance_matrix[i, j] = distance_metric(chord1, chord2)

    # Create vector space from pairwise distances using multidimensional scaling
    mds = MDS(n_components=3, dissimilarity="precomputed", random_state=0)
    vector_coordinates = mds.fit_transform(distance_matrix)

    # Save vectors per chord
    chords_with_vectors = []
    i = 0
    for chord_name in chords:
        for chord in chords[chord_name]:
            chords_with_vectors.append(
                {
                    "notes": chord,
                    "vector": vector_coordinates[i],
                    "chord_name": chord_name,
                    "octave": max(set([x[-1] for x in chord]), key=[x[-1] for x in chord].count)
                }
            )
            i += 1
    return chords_with_vectors, vector_coordinates


def generate_trinity_graph(chords, note_frequencies, save_graph=trinity_config.trinity_graph):
    """
    Save a graph as a JSON file, formatted specifically for visualization within the Trinity tool.
    """
    # Log progress
    logger.info("Generating and saving a Trinity graph object...")

    # Graph basics (hardcoded as Trinity input structure)
    network =  {
        "messageType": "GraphDirectedCollection",
        "graphId": "I Need To Grow Away From These Roots",
        "defaultNodeColor": "#0000FF88",
        "defaultEdgeColor": "#FFFFFFFF",
        "nodes": [],
        "edges": []
    }

    # Iterate through nodes, add to graph
    i = 0
    for chord_entry in chords:
        node = {
            "entityID": f"{i}",
            "vector": chord_entry["vector"].tolist(),
            "labels": [
                chord_entry["chord_name"],
                f'{chord_entry["notes"]}',
                f'octave: {chord_entry["octave"]}'
            ],
            "color": chord_color_mapping(chord_entry["chord_name"]),
            "properties": {
                "chord": chord_entry["chord_name"],
                "notes": chord_entry["notes"],
                "frequencies": [note_frequencies[x] for x in chord_entry["notes"]],
                "octave": chord_entry["octave"],
            }
        }
        network["nodes"].append(node)
        i += 1

    # Iterate through edges
    for chord1, chord2 in combinations(network["nodes"], 2):

        chord1_roots = [x[:-1] for x in chord1["properties"]["notes"]]
        chord2_roots = [x[:-1] for x in chord2["properties"]["notes"]]
        non_intersection = set(chord1_roots) ^ set(chord2_roots)  # allow less stringent edge conditions?
        if len(non_intersection) == 1:
            edge = {
                "startID": chord1["entityID"],
                "endID": chord2["entityID"],
                "color": "#88FFFFFF"
            }
            network["edges"].append(edge)

    # Save to file
    with open(save_graph, "w") as file:
        json.dump(network, file, indent=4)

    return network

def render_graph(network, vector_coordinates):
    """
    Generate plotly graph.
    """
    # Log progress
    logger.info("Rendering plotly preview...")

    # Create a DataFrame with coordinates, labels, and colors
    df = pd.DataFrame(vector_coordinates, columns=['x', 'y', 'z'])

    # Extract colors and labels for each node
    colors = [node["color"] for node in network["nodes"]]
    labels = ["\n ".join(node["labels"]) for node in network["nodes"]]  # Assuming single label

    # Initialize Plotly figure
    fig = go.Figure()

    # Add nodes with colors and hover labels, removing x, y, z from hoverinfo
    fig.add_trace(go.Scatter3d(
        x=df['x'], y=df['y'], z=df['z'],
        mode='markers',
        marker=dict(size=5, color=colors, opacity=0.8),
        hovertext=labels,
        hoverinfo="text",
        name='Nodes',
        showlegend=False
    ))

    # Add edges from network data
    for edge in network["edges"]:
        start = int(edge["startID"])
        end = int(edge["endID"])
        x0, y0, z0 = vector_coordinates[start]
        x1, y1, z1 = vector_coordinates[end]
        fig.add_trace(go.Scatter3d(
            x=[x0, x1], y=[y0, y1], z=[z0, z1],
            mode='lines',
            line=dict(color='gray', width=1),
            hoverinfo='none',
            showlegend=False
        ))

    # Layout adjustments
    fig.update_layout(
        title="I Need To Grow Away From These Roots",
        scene=dict(
            xaxis=dict(title='', showticklabels=False, color="white", showgrid=False, zeroline=False),
            yaxis=dict(title='', showticklabels=False, color="white", showgrid=False, zeroline=False),
            zaxis=dict(title='', showticklabels=False, color="white", showgrid=False, zeroline=False),
            bgcolor="white"sfghn
        ),
        showlegend=False
    )

    # Display graph
    fig.show()
