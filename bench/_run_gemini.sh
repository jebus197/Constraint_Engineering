#!/bin/bash
cd /Users/georgejackson/Developer_Projects/Constraint_Engineering
source .env
python3 bench/run_experiment.py --config gemini-flash --passes 3
