#!/usr/bin/env python3
"""
Quick script to run the pathfinding analysis
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("🤖 ROBOT PATHFINDING ALGORITHM COMPARISON")
print("=" * 50)
print("Starting comprehensive analysis...")
print("This will test 4 algorithms across 3 environments")
print("=" * 50)

try:
    from backend_runner import main
    main()
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure all required packages are installed:")
    print("pip install numpy matplotlib")
except Exception as e:
    print(f"Error during analysis: {e}")
