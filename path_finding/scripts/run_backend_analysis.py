#!/usr/bin/env python3
"""
Quick script to run backend pathfinding analysis.
"""

import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend_runner import main

if __name__ == "__main__":
    print("Starting Robot Pathfinding Backend Analysis...")
    print("This will run all algorithms and generate a backend report.\n")
    main()
    print("\nAnalysis finished! Check generated backend_report_*.txt")
