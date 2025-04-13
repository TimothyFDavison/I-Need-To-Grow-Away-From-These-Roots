import config
import utils
from . import trinity_utils


if __name__ == "__main__":

    # Get chords, chord graph. Will auto-generate if chords/graph file throws errors.
    if config.use_existing_files:
        chords = utils.load_chords()
        frequencies = utils.generate_frequencies()
    else:
        chords = utils.get_chords()
        frequencies = utils.generate_frequencies()

    # Compute pairwise distances of chord nodes
    chords_with_vectors, vector_coordinates = trinity_utils.generate_vector_space(chords)

    # Generate graph
    network = trinity_utils.generate_trinity_graph(chords_with_vectors, frequencies)

    # Visualize using plotly (for preliminary exploration prior to Trinity import)
    trinity_utils.render_graph(network, vector_coordinates)
