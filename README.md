## I Need To Grow Away From These Roots
Ambient music generation inspired by the audio component of David Whiting's artistic piece, [I Need To
Grow Away From These Roots](https://www.vitling.xyz/i-need-to-grow-away-from-these-roots/). 
All credit to the original artist. 

The principal script of this repository (`main.py`) will produce a network of chords and a ruleset by which to 
traverse those chords, then play that soundscape using Python's `simpleaudio` package.

The second component of this repository (`trinity.py`) transforms the chord network into a readable format for the
[Trinity 3D visualization tool](https://github.com/trinity-xai/Trinity). The chord network is also rendered as a 
3D network in `plotly` to serve as a preview.

## Usage
This module runs on Python 3.12. When run, the program will continue generating an ambient soundscape indefinitely. 
```bash
pip install -r requirements.txt
python main.py
```

## 

