#!/usr/bin/env python3
"""Unbounded 900 ships with overlapping contours; -webkit-text-stroke draws every contour, so the
outline names showed inner lines. This writes an overlap-free copy used ONLY for the Act-1 outline names."""
import os
from fontTools.ttLib import TTFont
from fontTools.ttLib.removeOverlaps import removeOverlaps
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../assets/mg1/fonts')
f = TTFont(os.path.join(D, 'Unbounded-900.ttf'))
removeOverlaps(f)
f.save(os.path.join(D, 'Unbounded-900-merged.ttf')); print('ok')
