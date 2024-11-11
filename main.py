import random
from multiprocessing import Process

import config
import utils


if __name__ == '__main__':

    # Get chords, chord graph. Will auto-generate if chords/graph file throws errors.
    if config.use_existing_files:
        chords = utils.load_chords()
        frequencies = utils.generate_frequencies()
        graph = utils.load_graph(chords, frequencies)
    else:
        chords = utils.get_chords()
        frequencies = utils.generate_frequencies()
        graph = utils.generate_graph(chords, frequencies)

    # Select an initial node, initiate the playback loop
    utils.logger.info("Initiating generative loop...")
    current_node = random.choice(list(graph.nodes()))
    audio_segments = []
    while True:

        # Create concurrently running audio threads
        process1 = Process(target=utils.play_base_chord, args=(graph, current_node,))
        process2 = Process(target=utils.play_supplement, args=(graph, current_node,))

        # Manage processes
        process1.start()
        process2.start()
        process1.join()
        process2.join()

        # Select new node
        random_edge = random.choice(list(graph.edges(current_node)))
        current_node = random_edge[1] if random_edge[0] == current_node else random_edge[0]
