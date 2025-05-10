# sat-solving-algorithms
This project contains Python implementations of three fundamental SAT-solving algorithms: Resolution, Davis-Putnam (DP) and Davis-Putnam-Logemann-Loveland (DPLL). It includes benchmark CNFs as well as output CSV files.

# Contents
- scripts/: Python implementations of the SAT solvers
- cnfs/: CNF benchmark files, organized by size
- results/: CSV files with the output of each solver
- README.md: Project overview
- LICENSE: MIT license

# Instructions: How to run
Python 3 is needed. To run a certain solver on a certain CNF folder, run this command (change accordingly):
```bash
python scripts/dpll.py cnfs/small

