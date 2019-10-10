#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
NEXOGEN GIS GeoPoint Dataclass
"""

from __future__ import annotations
__version__ = '0.1.0'

from dataclasses import dataclass

@dataclass
class GeoPoint:
    lat: float
    lon: float

