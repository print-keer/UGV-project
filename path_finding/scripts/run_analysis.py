#!/usr/bin/env python3
"""
Quick script to run backend pathfinding analysis.
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("ROBOT PATHFINDING BACKEND ANALYSIS")
print("=" * 50)

try:
    from backend_runner import main
    main()
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Install required packages:")
    print("pip install numpy matplotlib")
except Exception as e:
    print(f"Error during analysis: {e}")
