#!/usr/bin/env python
"""Simple brain test runner."""
import sys
import os

os.chdir(r"d:\Q-Bot-fx-\Q-Bot-FX")
sys.path.insert(0, ".")

from backend.brain.brain_test import run_all_tests

if __name__ == "__main__":
    results = run_all_tests()
    sys.exit(0 if all(results.values()) else 1)
