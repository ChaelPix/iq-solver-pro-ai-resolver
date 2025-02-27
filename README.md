# IQ Puzzler Pro Solver

An AI-powered solver for the IQ Puzzler Pro game using Knuth's Algorithm X with optimizations. This project was developed as part of IA41 at UTBM.

## Description
The solver can:
- Solve any IQ Puzzler Pro level configuration
- Generate and solve custom grid sizes beyond the original game
- Visualize the solving process
- Use different heuristics to optimize solving speed

## Setup

```bash
git clone https://github.com/ChaelPix/iq-solver-pro-ai-resolver.git
cd iq-solver-pro-ai-resolver
```

```bash
pip install -r requirements.txt
```

## Usage

Run the main program:
```bash
python src/main.py
```

The interface allows you to:
- Create or load game configurations
- Place pieces manually
- Choose solving heuristics
- Watch the solving process in real-time
- Generate custom grid sizes

## Requirements
- Python 3.8+
- Tkinter
- NumPy
- ttkbootstrap

## Authors
- Antoine PERRIN
- Traïan BEAUJARD

Algo x de knuth, ressources :
https://core.ac.uk/download/pdf/230920551.pdf
https://www.cs.mcgill.ca/~aassaf9/python/algorithm_x.html
https://en.wikipedia.org/wiki/Knuth%27s_Algorithm_X