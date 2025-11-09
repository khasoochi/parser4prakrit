#!/usr/bin/env python3
"""
Prakrit Word Games - Main Entry Point
A unified application for learning Prakrit through 5 integrated games.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import main

if __name__ == '__main__':
    main()
