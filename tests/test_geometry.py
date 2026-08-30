import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest
import numpy as np
from aeroopt.geometry.nose_cone import NoseConeGenerator
from aeroopt.geometry.drone_arm import DroneArmGenerator

def test_sears_haack_dimensions():
    gen = NoseConeGenerator(length=1.0, base_radius=0.1, num_points=50)
    x, y = gen.sears_haack()
    assert len(x) == 50
    assert len(y) == 50
    assert np.isclose(y[0], 0.0, atol=1e-3)
    assert np.isclose(y[-1], 0.1, atol=1e-3)

def test_drone_arm_dimensions():
    arm = DroneArmGenerator(chord_length=0.05, max_thickness=0.01)
    x, y = arm.teardrop_profile()
    assert len(x) == 100
    assert np.max(y) > 0.0
